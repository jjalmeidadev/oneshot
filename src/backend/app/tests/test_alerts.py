import asyncio
import hashlib
import hmac
import json
import sys
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

# Preserva a cobertura anterior do backend-api na selecao por marcador (#255).
pytestmark = pytest.mark.integration
from fastapi.testclient import TestClient

from app.alerts.errors import AlertConflictError, AlertMessageError
from app.alerts.messaging import (
    DELIVERY_ROUTING_KEY,
    ROUTING_KEYS,
    SHAREPOINT_ROUTING_KEY,
    Message,
    RabbitMQBroker,
)
from app.alerts.repository import InMemoryAlertRepository
from app.alerts.repository import reset_alert_repository
from app.alerts.schemas import (
    AlertNotification,
    AlertRule,
    AnswerAlertWorkflowRequest,
    ConfirmAlertWorkflowRequest,
    CreateAlertRequest,
    PrepareAlertRequest,
    ScheduleItem,
    StartAlertWorkflowRequest,
)
from app.alerts.service import AlertService
from app.alerts.service import get_alert_service
from app.alerts.source import ScheduleSource, get_schedule_source
from app.alerts.workflow import AlertWorkflowService, get_alert_workflow_service
from app.alerts.worker import process_delivery_message
from app.main import app
from app.reports.security import ReportIdentity


DELIVERY_CALLBACK_SECRET = "REDACTED_FOR_PUBLIC_RELEASE"
DELIVERY_CALLBACK_PATH = "/api/integrations/notifications/delivery-results"


def _delivery_body(payload: dict) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _delivery_signature(body: bytes, secret: str = DELIVERY_CALLBACK_SECRET) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _post_delivery_callback(
    client: TestClient,
    payload: dict,
    *,
    signature: str | None = None,
    signed_body: bytes | None = None,
):
    body = _delivery_body(payload)
    return client.post(
        DELIVERY_CALLBACK_PATH,
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature
            if signature is not None
            else _delivery_signature(signed_body or body),
        },
    )


class FixedSource(ScheduleSource):
    def list_projects(self):
        return [{"id": "PRJ-1", "label": "Projeto Um"}]

    def list_items(self, project_id):
        return [
            ScheduleItem(
                item_id="late",
                project_id=project_id,
                description="Entrega atrasada",
                planned_end_date=date(2026, 9, 1),
                progress_percent=80,
                status="em_andamento",
                updated_at=datetime(2026, 9, 20, tzinfo=timezone.utc),
                source="test://late",
            ),
            ScheduleItem(
                item_id="done",
                project_id=project_id,
                description="Entrega concluida",
                planned_end_date=date(2026, 8, 1),
                progress_percent=100,
                status="concluido",
                updated_at=datetime(2026, 9, 20, tzinfo=timezone.utc),
                source="test://done",
            ),
        ]


@pytest.fixture
def identity(monkeypatch):
    monkeypatch.setenv(
        "REPORT_SIMULATED_IDENTITIES",
        '{"token":{"subject":"user-1","display_name":"Usuario","role":"pmo","can_export":true,"allow_all":true}}',
    )
    return ReportIdentity("user-1", "Usuario", "pmo", True, True, frozenset(), frozenset())


@pytest.fixture
def setup(identity):
    repository = InMemoryAlertRepository()
    service = AlertService(repository, FixedSource(), secret=b"test-secret")
    return repository, service


def create_subscription(service, identity, threshold=7):
    prepared = service.prepare(
        PrepareAlertRequest(
            conversation_id="conversation-1",
            rule=AlertRule(project_id="PRJ-1", project_label="Projeto Um", threshold_days=threshold),
        ),
        identity,
    )
    return service.create(
        CreateAlertRequest(
            prepared_alert=prepared.prepared_alert,
            confirmation_hash=prepared.confirmation_hash,
            idempotency_key="test-key-123",
        ),
        identity,
    )


def test_confirmation_and_creation_are_idempotent(setup, identity):
    _, service = setup
    first, created = create_subscription(service, identity)
    second, repeated = create_subscription(service, identity)
    assert created is True
    assert repeated is False
    assert second.subscription_id == first.subscription_id


def test_tampered_confirmation_is_rejected(setup, identity):
    _, service = setup
    prepared = service.prepare(
        PrepareAlertRequest(conversation_id="c", rule=AlertRule(project_id="PRJ-1", project_label="Projeto Um", threshold_days=7)), identity
    )
    with pytest.raises(AlertConflictError):
        service.create(CreateAlertRequest(prepared_alert=prepared.prepared_alert, confirmation_hash="0" * 64, idempotency_key="tampered-1"), identity)


def test_evaluation_matches_only_overdue_open_item(setup, identity):
    repository, service = setup
    subscription, _ = create_subscription(service, identity)
    evaluation = service.evaluate(subscription.subscription_id, date(2026, 9, 22))
    assert evaluation.outcome.value == "matched"
    assert evaluation.eligible_count == 1
    requested = [item for item in repository.outbox if item["event_type"] == "alert.notification.requested"]
    assert len(requested) == 1
    payload = requested[0]["payload"]
    notification = AlertNotification.model_validate(payload["notification"])
    assert repository.create_notification(notification, payload["episode_key"]) is True
    assert repository.create_notification(notification, payload["episode_key"]) is False
    assert service.notifications(identity).unread_count == 1


def test_threshold_boundary_is_strict(setup, identity):
    _, service = setup
    subscription, _ = create_subscription(service, identity, threshold=21)
    evaluation = service.evaluate(subscription.subscription_id, date(2026, 9, 22))
    assert evaluation.outcome.value == "not_matched"


class MissingDateSource(ScheduleSource):
    def list_projects(self):
        return [{"id": "PRJ-1", "label": "Projeto Um"}]

    def list_items(self, project_id):
        return [
            ScheduleItem(
                item_id="sem-data",
                project_id=project_id,
                description="Entrega sem data planejada",
                planned_end_date=None,
                progress_percent=10,
                status="em_andamento",
                updated_at=datetime(2026, 9, 20, tzinfo=timezone.utc),
                source="test://missing",
            ),
        ]


def test_missing_data_yields_indeterminate(identity):
    repository = InMemoryAlertRepository()
    service = AlertService(repository, MissingDateSource(), secret=b"test-secret")
    subscription, _ = create_subscription(service, identity)
    evaluation = service.evaluate(subscription.subscription_id, date(2026, 9, 22))
    assert evaluation.outcome.value == "indeterminate"


def test_schedule_due_enqueues_and_updates_atomically(setup, identity):
    repository, service = setup
    subscription, _ = create_subscription(service, identity)
    # Antecipa a proxima avaliacao para tornar a inscricao elegivel ao scheduler.
    stored = repository.get_subscription(subscription.subscription_id)
    stored.next_evaluation_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    repository.save_subscription(stored, stored.revision)
    scheduled = service.schedule_due(now=datetime(2026, 9, 22, 12, tzinfo=timezone.utc))
    assert subscription.subscription_id in scheduled
    events = [item for item in repository.outbox if item["event_type"] == "alert.evaluation.requested"]
    assert len(events) == 1
    updated = repository.get_subscription(subscription.subscription_id)
    assert updated.revision == stored.revision + 1


def test_resend_bucket_anchors_on_threshold_crossing(setup, identity):
    _, service = setup
    subscription, _ = create_subscription(service, identity, threshold=7)
    subscription.rule.resend_interval_days = 7
    repository = service.repository
    item = FixedSource().list_items("PRJ-1")[0]
    # overdue de 8 dias: 1 dia alem do limiar -> primeiro episodio (bucket 0).
    service._notify(subscription, item, overdue=8, reference=date(2026, 9, 9))
    # overdue de 15 dias: 8 dias alem do limiar -> segundo episodio (bucket 1).
    service._notify(subscription, item, overdue=15, reference=date(2026, 9, 16))
    buckets = {entry["payload"]["episode_key"].rsplit(":", 1)[-1] for entry in repository.outbox if entry["event_type"] == "alert.notification.requested"}
    assert buckets == {"0", "1"}


def test_subscription_created_is_not_enqueued(setup, identity):
    repository, service = setup
    create_subscription(service, identity)
    created_events = [item for item in repository.outbox if item["event_type"] == "alert.subscription.created"]
    assert created_events == []


def test_guided_workflow_reaches_active_subscription(setup, identity):
    repository, service = setup
    workflow = AlertWorkflowService(repository, service)
    current = workflow.start(StartAlertWorkflowRequest(conversation_id="chat-1"), identity)
    answers = [("project", "PRJ-1"), ("threshold", 7), ("schedule", "daily"), ("resend", "none")]
    for index, (step, answer) in enumerate(answers):
        current = workflow.answer(current.session_id, AnswerAlertWorkflowRequest(step=step, value=answer, revision=current.revision, client_action_id=f"action-{index}"), identity)
    assert current.status.value == "ready_for_confirmation"
    current = workflow.confirm(current.session_id, ConfirmAlertWorkflowRequest(revision=current.revision, client_action_id="confirm-1"), identity)
    assert current.status.value == "completed"
    assert current.subscription is not None
    assert current.subscription.status.value == "active"


def test_http_contract_configures_and_lists_alert(monkeypatch):
    monkeypatch.setenv("ALERT_REPOSITORY_MODE", "memory")
    monkeypatch.setenv("ALERT_SCHEDULE_SOURCE", "synthetic")
    monkeypatch.setenv(
        "REPORT_SIMULATED_IDENTITIES",
        '{"token":{"subject":"user-http","display_name":"Usuario HTTP","role":"pmo","can_export":true,"allow_all":true}}',
    )
    reset_alert_repository()
    get_schedule_source.cache_clear()
    get_alert_service.cache_clear()
    get_alert_workflow_service.cache_clear()
    headers = {"Authorization": "Bearer token"}
    with TestClient(app) as client:
        response = client.post(
            "/api/alert-workflow-sessions",
            headers=headers,
            json={"contract_version": "1.0", "conversation_id": "http-chat", "parameters": {}},
        )
        assert response.status_code == 201
        workflow = response.json()
        for index, (step, answer) in enumerate(
            [("project", "PRJ-SINALIZACAO"), ("threshold", 7), ("schedule", "daily"), ("resend", "none")]
        ):
            response = client.post(
                f"/api/alert-workflow-sessions/{workflow['session_id']}/answers",
                headers=headers,
                json={"step": step, "value": answer, "revision": workflow["revision"], "client_action_id": f"http-action-{index}"},
            )
            assert response.status_code == 200
            workflow = response.json()
        response = client.post(
            f"/api/alert-workflow-sessions/{workflow['session_id']}/confirm",
            headers=headers,
            json={"revision": workflow["revision"], "client_action_id": "http-confirm"},
        )
        assert response.status_code == 200
        assert response.json()["subscription"]["status"] == "active"
        listed = client.get("/api/alert-subscriptions", headers=headers)
        assert listed.status_code == 200
        assert len(listed.json()) == 1


@pytest.fixture
def delivery_callback_context(monkeypatch):
    monkeypatch.setenv("ALERT_REPOSITORY_MODE", "memory")
    monkeypatch.setenv("ALERT_SCHEDULE_SOURCE", "synthetic")
    monkeypatch.setenv("NOTIFICATION_CALLBACK_SECRET", DELIVERY_CALLBACK_SECRET)
    reset_alert_repository()
    get_schedule_source.cache_clear()
    get_alert_service.cache_clear()
    repository = get_alert_service().repository
    notification = AlertNotification(
        notification_id="1674b3e9-ecba-4a78-a50f-848f5eaf0d79",
        correlation_id="delivery-correlation",
        subscription_id="delivery-subscription",
        occurrence_id="delivery-occurrence",
        recipient_subject="delivery-user",
        project_id="PRJ-1",
        item_id="delivery-item",
        title="Entrega pendente",
        body="Notificacao usada no contrato de callback.",
        reference_date=date(2026, 9, 25),
        overdue_days=1,
        created_at=datetime(2026, 9, 25, 11, tzinfo=timezone.utc),
    )
    assert repository.create_notification(notification, "delivery-episode") is True
    payload = {
        "callback_id": "delivery-callback-001",
        "notification_id": notification.notification_id,
        "provider": "simulated",
        "status": "delivered",
        "attempted_at": "2026-09-25T12:00:00Z",
        "error_code": None,
    }
    with TestClient(app) as client:
        yield client, repository, payload
    reset_alert_repository()
    get_alert_service.cache_clear()


def test_delivery_callback_succeeds(delivery_callback_context):
    client, repository, payload = delivery_callback_context
    response = _post_delivery_callback(client, payload)
    assert response.status_code == 200
    assert response.json()["callback_id"] == payload["callback_id"]
    assert response.json()["status"] == "delivered"
    assert response.json()["received_at"]
    assert len(repository.outbox) == 1
    event = repository.outbox[0]
    assert event["event_type"] == DELIVERY_ROUTING_KEY
    assert event["payload"] == payload
    assert event["correlation_id"] == "delivery-correlation"
    assert repository.delivery_attempts == []


@pytest.mark.parametrize(
    "signature",
    [None, "", "invalid", "sha256=short", f"sha256={'z' * 64}"],
)
def test_delivery_callback_rejects_invalid_signature(
    delivery_callback_context, signature
):
    client, _, payload = delivery_callback_context
    body = _delivery_body(payload)
    headers = {"Content-Type": "application/json"}
    if signature is not None:
        headers["X-Webhook-Signature"] = signature
    response = client.post(
        DELIVERY_CALLBACK_PATH,
        content=body,
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOTIFICATION_CALLBACK_UNAUTHORIZED"


def test_delivery_callback_rejects_signature_for_another_body(
    delivery_callback_context,
):
    client, _, payload = delivery_callback_context
    original_body = _delivery_body(payload)
    response = _post_delivery_callback(
        client,
        {**payload, "provider": "tampered"},
        signed_body=original_body,
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOTIFICATION_CALLBACK_UNAUTHORIZED"


def test_delivery_callback_requires_configured_secret(
    delivery_callback_context, monkeypatch
):
    client, _, payload = delivery_callback_context
    monkeypatch.delenv("NOTIFICATION_CALLBACK_SECRET")
    response = _post_delivery_callback(client, payload)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ALERT_CONFIGURATION_ERROR"


def test_delivery_callback_rejects_invalid_payload(delivery_callback_context):
    client, _, payload = delivery_callback_context
    response = _post_delivery_callback(
        client,
        {**payload, "notification_id": "not-a-uuid", "unexpected": True},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ALERT_INVALID_INPUT"


def test_delivery_callback_is_idempotent(delivery_callback_context):
    client, repository, payload = delivery_callback_context
    first = _post_delivery_callback(client, payload)
    repeated = _post_delivery_callback(client, payload)
    assert first.status_code == repeated.status_code == 200
    assert first.json() == repeated.json()
    assert len(repository.delivery_callbacks) == 1
    assert len(repository.outbox) == 1
    message = Message(**repository.outbox[0])
    assert process_delivery_message(message, repository) is True
    assert process_delivery_message(message, repository) is False
    assert len(repository.delivery_attempts) == 1


def test_delivery_callback_rejects_conflicting_callback_id(
    delivery_callback_context,
):
    client, _, payload = delivery_callback_context
    assert _post_delivery_callback(client, payload).status_code == 200
    response = _post_delivery_callback(
        client,
        {**payload, "status": "failed", "error_code": "PROVIDER_ERROR"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ALERT_CONFLICT"


def test_delivery_callback_rejects_unknown_notification(
    delivery_callback_context,
):
    client, _, payload = delivery_callback_context
    response = _post_delivery_callback(
        client,
        {
            **payload,
            "callback_id": "delivery-callback-unknown",
            "notification_id": "b74a1986-b955-49d7-a922-6bd1c6125df0",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOTIFICATION_NOT_FOUND"


def test_delivery_callback_persists_payload_in_memory(delivery_callback_context):
    client, repository, payload = delivery_callback_context
    response = _post_delivery_callback(client, payload)
    stored = repository.delivery_callbacks[payload["callback_id"]]
    assert response.status_code == 200
    assert len(stored["payload_hash"]) == 64
    assert stored["callback_payload"] == payload
    received_at = datetime.fromisoformat(
        response.json()["received_at"].replace("Z", "+00:00")
    )
    assert stored["value"].received_at == received_at


def test_rabbitmq_topology_keeps_existing_routes_and_adds_delivery():
    assert ROUTING_KEYS == (
        "alert.evaluation.requested",
        "alert.notification.requested",
        "notification.delivery.received",
        "sharepoint.change.received",
    )


def test_publisher_uses_delivery_routing_key_without_real_rabbitmq(monkeypatch):
    class ExchangeDouble:
        def __init__(self):
            self.routing_keys = []

        async def publish(self, _message, routing_key):
            self.routing_keys.append(routing_key)

    broker = RabbitMQBroker("amqp://unused")
    exchange = ExchangeDouble()
    broker.exchange = exchange
    monkeypatch.setitem(
        sys.modules,
        "aio_pika",
        SimpleNamespace(
            Message=lambda **values: values,
            DeliveryMode=SimpleNamespace(PERSISTENT=2),
        ),
    )
    asyncio.run(
        broker.publish(
            Message(
                event_id="d0af886f-8438-4540-a773-4aa33015139b",
                event_type=DELIVERY_ROUTING_KEY,
                correlation_id="delivery-correlation",
                payload={},
            )
        )
    )
    assert exchange.routing_keys == [DELIVERY_ROUTING_KEY]


def test_delivery_consumer_records_success(delivery_callback_context):
    client, repository, payload = delivery_callback_context
    response = _post_delivery_callback(client, payload)
    assert response.status_code == 200
    assert process_delivery_message(Message(**repository.outbox[0]), repository)
    assert repository.delivery_attempts == [
        {
            "notification_id": payload["notification_id"],
            "callback_id": payload["callback_id"],
            "channel": "simulated",
            "attempt_number": 1,
            "status": "available",
            "error_code": None,
            "attempted_at": datetime(2026, 9, 25, 12, tzinfo=timezone.utc),
        }
    ]


def test_delivery_consumer_records_failure(delivery_callback_context):
    client, repository, payload = delivery_callback_context
    failed = {
        **payload,
        "callback_id": "delivery-callback-failed",
        "status": "failed",
        "error_code": "PROVIDER_UNAVAILABLE",
    }
    response = _post_delivery_callback(client, failed)
    assert response.status_code == 200
    assert process_delivery_message(Message(**repository.outbox[0]), repository)
    attempt = repository.delivery_attempts[0]
    assert attempt["status"] == "failed"
    assert attempt["error_code"] == "PROVIDER_UNAVAILABLE"


def test_delivery_consumer_rejects_invalid_event(delivery_callback_context):
    _, repository, _ = delivery_callback_context
    invalid = Message(
        event_id="not-a-uuid",
        event_type=DELIVERY_ROUTING_KEY,
        correlation_id="delivery-correlation",
        payload={"callback_id": "incomplete-callback"},
    )
    with pytest.raises(AlertMessageError) as error:
        process_delivery_message(invalid, repository)
    assert error.value.code == "ALERT_INVALID_MESSAGE"
    assert repository.delivery_attempts == []
