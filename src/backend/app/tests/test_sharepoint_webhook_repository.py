"""Idempotência e contrato de persistência do webhook SharePoint."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import pytest

from app.sharepoint_webhooks.repository import (
    InMemorySharePointWebhookRepository,
    PostgresSharePointWebhookRepository,
    SharePointWebhookConflictError,
)
from app.sharepoint_webhooks.schemas import SharePointNotificationBatch


ROOT = Path(__file__).resolve().parents[4]
EVENT_ID = "d6a29bb6-9d2d-40dd-aa3f-20dc8d7a1218"
CLIENT_STATE = "segredo-que-nao-pode-ser-persistido"


class FakeCursor:
    def __init__(self, state):
        self.state = state
        self.row = None
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        normalized = " ".join(query.split())
        event_id = str(params[0])
        if normalized.startswith("INSERT INTO"):
            if event_id in self.state:
                self.row = None
            else:
                self.state[event_id] = {
                    "payload_hash": params[9],
                    "payload": json.loads(params[10]),
                    "processing_status": "pending",
                }
                self.row = (event_id,)
            return
        stored = self.state.get(event_id)
        if "SELECT payload_hash" in normalized:
            self.row = (stored["payload_hash"],) if stored else None
            return
        if "SELECT payload" in normalized:
            self.row = (stored["payload"],) if stored else None
            return
        if normalized.startswith("SELECT event_id::text"):
            limit = int(params[0])
            self.rows = [
                (stored_event_id, item["payload"])
                for stored_event_id, item in self.state.items()
                if item["processing_status"] == "pending"
            ][:limit]
            return
        if normalized.startswith("UPDATE public.sharepoint_webhook_events"):
            if stored and stored["processing_status"] == "pending":
                stored["processing_status"] = "published"
                self.row = (event_id,)
            else:
                self.row = None
            return
        raise AssertionError(f"SQL inesperado: {normalized}")

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self):
        self.state = {}
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return FakeCursor(self.state)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        pass


def event(change_type: str = "updated"):
    batch = SharePointNotificationBatch.model_validate(
        {
            "value": [
                {
                    "eventId": EVENT_ID,
                    "subscriptionId": "sharepoint-mock-documents",
                    "clientState": CLIENT_STATE,
                    "changeType": change_type,
                    "resource": "lists/documentos_projetos/items/5101",
                    "resourceData": {
                        "siteId": "metro-sp-mock",
                        "listId": "documentos_projetos",
                        "itemId": 5101,
                        "partnerSourceId": (
                            "sharepoint-mock:documentos_projetos:5101"
                        ),
                    },
                    "occurredAt": "2026-10-07T12:30:00-03:00",
                }
            ]
        }
    )
    return batch.value[0]


def test_repository_does_not_persist_client_state():
    repository = InMemorySharePointWebhookRepository()
    repository.store_batch([event()])

    stored = repository.get_payload(EVENT_ID)

    assert stored is not None
    assert "clientState" not in stored
    assert CLIENT_STATE not in json.dumps(stored)


def test_conflicting_batch_is_atomic():
    repository = InMemorySharePointWebhookRepository()
    original = event()
    repository.store_batch([original])

    with pytest.raises(SharePointWebhookConflictError):
        repository.store_batch([event("deleted")])

    assert repository.get_payload(EVENT_ID)["changeType"] == "updated"


def test_concurrent_repetition_creates_exactly_one_event():
    repository = InMemorySharePointWebhookRepository()
    notification = event()

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(
            executor.map(lambda _index: repository.store_batch([notification]), range(16))
        )

    assert sum(result.created for result in results) == 1
    assert sum(result.duplicates for result in results) == 15
    assert repository.get_payload(EVENT_ID) is not None


def test_pending_event_is_exposed_once_until_marked_as_published():
    repository = InMemorySharePointWebhookRepository()
    repository.store_batch([event()])

    pending = repository.list_pending()

    assert [item.event_id for item in pending] == [EVENT_ID]
    assert CLIENT_STATE not in json.dumps(pending[0].payload)
    assert repository.mark_published(EVENT_ID) is True
    assert repository.mark_published(EVENT_ID) is False
    assert repository.list_pending() == []


def test_postgres_repository_uses_on_conflict_and_detects_collision(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/database")
    repository = PostgresSharePointWebhookRepository(
        connect=lambda *_args, **_kwargs: connection
    )

    first = repository.store_batch([event()])
    repeated = repository.store_batch([event()])

    assert first.created == 1
    assert repeated.duplicates == 1
    assert CLIENT_STATE not in json.dumps(repository.get_payload(EVENT_ID))
    assert [item.event_id for item in repository.list_pending()] == [EVENT_ID]
    assert repository.mark_published(EVENT_ID) is True
    assert repository.mark_published(EVENT_ID) is False
    assert repository.list_pending() == []
    with pytest.raises(SharePointWebhookConflictError):
        repository.store_batch([event("deleted")])
    assert connection.rollbacks == 1


def test_migration_defines_unique_inbox_and_pending_index():
    sql = (
        ROOT / "src/database/sql/22_sharepoint_webhook_events.sql"
    ).read_text(encoding="utf-8")

    assert "event_id UUID PRIMARY KEY" in sql
    assert "processing_status VARCHAR(16) NOT NULL DEFAULT 'pending'" in sql
    assert "sharepoint_webhook_events_pending_idx" in sql
    assert "ENABLE ROW LEVEL SECURITY" in sql
    assert "REVOKE ALL ON public.sharepoint_webhook_events" in sql
