from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.alerts.errors import AlertConflictError
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
from app.main import app
from app.reports.security import ReportIdentity


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
