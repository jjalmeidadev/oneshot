"""Topologia e produtor RabbitMQ do webhook SharePoint."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from threading import Lock

import pytest

from app.alerts.messaging import (
    Message,
    RabbitMQBroker,
    ROUTING_KEYS,
    SHAREPOINT_ROUTING_KEY,
)
from app.sharepoint_webhooks.consumer import (
    SharePointWebhookMessageError,
    process_sharepoint_change_message,
)
from app.sharepoint_webhooks.publisher import publish_pending_sharepoint_once
from app.sharepoint_webhooks.repository import InMemorySharePointWebhookRepository
from app.sharepoint_webhooks.schemas import SharePointNotificationBatch


EVENT_ID = "d6a29bb6-9d2d-40dd-aa3f-20dc8d7a1218"
ROOT = Path(__file__).resolve().parents[4]


def notification():
    return SharePointNotificationBatch.model_validate(
        {
            "value": [
                {
                    "eventId": EVENT_ID,
                    "subscriptionId": "sharepoint-mock-documents",
                    "clientState": "segredo-nao-publicado",
                    "changeType": "updated",
                    "resource": "lists/documentos_projetos/items/5101",
                    "resourceData": {
                        "siteId": "metro-sp-mock",
                        "listId": "documentos_projetos",
                        "itemId": 5101,
                        "partnerSourceId": "sharepoint-mock:documentos_projetos:5101",
                    },
                    "occurredAt": "2026-10-07T12:30:00-03:00",
                }
            ]
        }
    ).value[0]


class BrokerDouble:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.messages = []

    async def publish(self, message):
        if self.fail:
            raise RuntimeError("broker indisponível")
        self.messages.append(message)


class IncomingDouble:
    def __init__(self, message, *, redelivered):
        self.body = json.dumps(message.__dict__).encode("utf-8")
        self.redelivered = redelivered
        self.requeue = None

    def process(self, *, requeue):
        self.requeue = requeue
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False


class IteratorDouble:
    def __init__(self, incoming):
        self.incoming = incoming
        self.delivered = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.delivered:
            raise StopAsyncIteration
        self.delivered = True
        return self.incoming


class QueueDouble:
    def __init__(self, incoming):
        self.incoming = incoming

    def iterator(self):
        return IteratorDouble(self.incoming)


class ChannelDouble:
    def __init__(self, incoming):
        self.incoming = incoming

    async def get_queue(self, _routing_key):
        return QueueDouble(self.incoming)


def published_event():
    repository = InMemorySharePointWebhookRepository()
    repository.store_batch([notification()])
    broker = BrokerDouble()
    asyncio.run(
        publish_pending_sharepoint_once(repository=repository, broker=broker)
    )
    return repository, broker.messages[0]


def test_topology_adds_sharepoint_queue_and_automatic_dlq():
    assert SHAREPOINT_ROUTING_KEY == "sharepoint.change.received"
    assert SHAREPOINT_ROUTING_KEY in ROUTING_KEYS
    assert f"{SHAREPOINT_ROUTING_KEY}.dead" == "sharepoint.change.received.dead"


def test_publisher_sends_sanitized_event_and_marks_it_published():
    repository = InMemorySharePointWebhookRepository()
    repository.store_batch([notification()])
    broker = BrokerDouble()

    published = asyncio.run(
        publish_pending_sharepoint_once(repository=repository, broker=broker)
    )

    assert published == 1
    assert repository.list_pending() == []
    assert len(broker.messages) == 1
    message = broker.messages[0]
    assert message.event_id == EVENT_ID
    assert message.event_type == SHAREPOINT_ROUTING_KEY
    assert message.correlation_id == "sharepoint-mock-documents"
    assert "clientState" not in message.payload


def test_publish_failure_keeps_event_pending_for_retry():
    repository = InMemorySharePointWebhookRepository()
    repository.store_batch([notification()])

    published = asyncio.run(
        publish_pending_sharepoint_once(
            repository=repository,
            broker=BrokerDouble(fail=True),
        )
    )

    assert published == 0
    assert [item.event_id for item in repository.list_pending()] == [EVENT_ID]


def test_repeated_publisher_run_does_not_publish_again():
    repository = InMemorySharePointWebhookRepository()
    repository.store_batch([notification()])
    broker = BrokerDouble()

    first = asyncio.run(
        publish_pending_sharepoint_once(repository=repository, broker=broker)
    )
    second = asyncio.run(
        publish_pending_sharepoint_once(repository=repository, broker=broker)
    )

    assert (first, second) == (1, 0)
    assert len(broker.messages) == 1


def test_consumer_reindexes_source_and_marks_event_processed():
    repository, message = published_event()
    sources = []

    processed = process_sharepoint_change_message(
        message,
        repository=repository,
        reindex_source=sources.append,
    )

    assert processed is True
    assert sources == ["sharepoint-mock:documentos_projetos:5101"]
    assert repository.get_processing_status(EVENT_ID) == "processed"


def test_repeated_consumer_delivery_does_not_reindex_again():
    repository, message = published_event()
    sources = []

    first = process_sharepoint_change_message(
        message, repository=repository, reindex_source=sources.append
    )
    repeated = process_sharepoint_change_message(
        message, repository=repository, reindex_source=sources.append
    )

    assert (first, repeated) == (True, False)
    assert sources == ["sharepoint-mock:documentos_projetos:5101"]


def test_concurrent_consumer_delivery_produces_one_reindex_effect():
    repository, message = published_event()
    calls = 0
    lock = Lock()

    def reindex(_source_id):
        nonlocal calls
        with lock:
            calls += 1

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(
            executor.map(
                lambda _index: process_sharepoint_change_message(
                    message,
                    repository=repository,
                    reindex_source=reindex,
                ),
                range(16),
            )
        )

    assert sum(results) == 1
    assert calls == 1


def test_invalid_message_is_rejected_before_reindex():
    repository, message = published_event()
    invalid = Message(
        event_id=message.event_id,
        event_type="sharepoint.change.invalid",
        correlation_id=message.correlation_id,
        payload=message.payload,
    )
    sources = []

    with pytest.raises(SharePointWebhookMessageError):
        process_sharepoint_change_message(
            invalid,
            repository=repository,
            reindex_source=sources.append,
        )

    assert sources == []
    assert repository.get_processing_status(EVENT_ID) == "published"


def test_message_divergent_from_inbox_is_rejected():
    repository, message = published_event()
    changed_payload = {**message.payload, "changeType": "deleted"}
    divergent = Message(
        event_id=message.event_id,
        event_type=message.event_type,
        correlation_id=message.correlation_id,
        payload=changed_payload,
    )

    with pytest.raises(SharePointWebhookMessageError):
        process_sharepoint_change_message(
            divergent,
            repository=repository,
            reindex_source=lambda _source_id: None,
        )


def test_reindex_failure_retries_once_then_marks_event_failed():
    repository, message = published_event()

    def fail(_source_id):
        raise RuntimeError("falha controlada")

    with pytest.raises(RuntimeError):
        process_sharepoint_change_message(
            message, repository=repository, reindex_source=fail
        )
    assert repository.get_processing_status(EVENT_ID) == "published"

    with pytest.raises(RuntimeError):
        process_sharepoint_change_message(
            message, repository=repository, reindex_source=fail
        )
    assert repository.get_processing_status(EVENT_ID) == "failed"
    assert (
        process_sharepoint_change_message(
            message, repository=repository, reindex_source=fail
        )
        is False
    )


def test_redelivered_invalid_message_is_rejected_for_dlq():
    invalid = Message(
        event_id=EVENT_ID,
        event_type="sharepoint.change.invalid",
        correlation_id="sharepoint-mock-documents",
        payload={},
    )
    incoming = IncomingDouble(invalid, redelivered=True)
    broker = RabbitMQBroker("amqp://unused")
    broker.channel = ChannelDouble(incoming)

    async def reject(_message):
        raise SharePointWebhookMessageError("mensagem inválida")

    with pytest.raises(SharePointWebhookMessageError):
        asyncio.run(broker.consume(SHAREPOINT_ROUTING_KEY, reject))

    assert incoming.requeue is False


def test_production_compose_runs_sharepoint_workers_with_persistent_mode():
    compose = (ROOT / "compose.prod.yml").read_text(encoding="utf-8")

    assert "sharepoint-publisher:" in compose
    assert "app.sharepoint_webhooks.worker, publisher" in compose
    assert "sharepoint-consumer:" in compose
    assert "app.sharepoint_webhooks.worker, consumer" in compose
    assert "SHAREPOINT_WEBHOOK_REPOSITORY_MODE: database" in compose
    assert "NOTIFICATION_CALLBACK_SECRET:" in compose
    assert "NOTIFICATION_CALLBACK_TOKEN:" not in compose
