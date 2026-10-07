"""Inbox idempotente dos eventos do SharePoint simulado."""

from __future__ import annotations

import hashlib
import json
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from threading import RLock
from typing import Any, Callable

from app.database.connection import open_database_connection
from app.sharepoint_webhooks.schemas import SharePointChangeNotification


class SharePointWebhookConflictError(RuntimeError):
    """O mesmo eventId foi reutilizado com conteúdo diferente."""


class SharePointWebhookStorageError(RuntimeError):
    """A inbox não pôde persistir o lote recebido."""


@dataclass(frozen=True)
class StoreBatchResult:
    received: int
    created: int
    duplicates: int


@dataclass(frozen=True)
class PendingSharePointEvent:
    event_id: str
    payload: dict[str, Any]


class SharePointWebhookRepository(ABC):
    @abstractmethod
    def store_batch(
        self, events: list[SharePointChangeNotification]
    ) -> StoreBatchResult:
        raise NotImplementedError

    @abstractmethod
    def get_payload(self, event_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def list_pending(self, limit: int = 100) -> list[PendingSharePointEvent]:
        raise NotImplementedError

    @abstractmethod
    def mark_published(self, event_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def claim_for_processing(self, event_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def mark_processed(self, event_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def mark_processing_failed(self, event_id: str, error_code: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_processing_status(self, event_id: str) -> str | None:
        raise NotImplementedError


class InMemorySharePointWebhookRepository(SharePointWebhookRepository):
    def __init__(self) -> None:
        self._events: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def store_batch(
        self, events: list[SharePointChangeNotification]
    ) -> StoreBatchResult:
        with self._lock:
            staged = deepcopy(self._events)
            created = 0
            duplicates = 0
            for event in events:
                event_id = str(event.event_id)
                payload = sanitized_payload(event)
                payload_hash = hash_payload(payload)
                existing = staged.get(event_id)
                if existing is not None:
                    if existing["payload_hash"] != payload_hash:
                        raise SharePointWebhookConflictError(
                            "eventId pertence a outra notificação."
                        )
                    duplicates += 1
                    continue
                staged[event_id] = {
                    "payload_hash": payload_hash,
                    "payload": payload,
                    "processing_status": "pending",
                    "failure_count": 0,
                    "last_error_code": None,
                }
                created += 1
            self._events = staged
        return StoreBatchResult(len(events), created, duplicates)

    def get_payload(self, event_id: str) -> dict[str, Any] | None:
        with self._lock:
            stored = self._events.get(event_id)
            return deepcopy(stored["payload"]) if stored else None

    def list_pending(self, limit: int = 100) -> list[PendingSharePointEvent]:
        bounded_limit = _bounded_limit(limit)
        with self._lock:
            return [
                PendingSharePointEvent(event_id=event_id, payload=deepcopy(stored["payload"]))
                for event_id, stored in self._events.items()
                if stored["processing_status"] == "pending"
            ][:bounded_limit]

    def mark_published(self, event_id: str) -> bool:
        with self._lock:
            stored = self._events.get(event_id)
            if stored is None or stored["processing_status"] != "pending":
                return False
            stored["processing_status"] = "published"
            return True

    def claim_for_processing(self, event_id: str) -> bool:
        with self._lock:
            stored = self._events.get(event_id)
            if stored is None or stored["processing_status"] != "published":
                return False
            stored["processing_status"] = "processing"
            return True

    def mark_processed(self, event_id: str) -> bool:
        with self._lock:
            stored = self._events.get(event_id)
            if stored is None or stored["processing_status"] != "processing":
                return False
            stored["processing_status"] = "processed"
            stored["last_error_code"] = None
            return True

    def mark_processing_failed(self, event_id: str, error_code: str) -> bool:
        with self._lock:
            stored = self._events.get(event_id)
            if stored is None or stored["processing_status"] != "processing":
                return False
            stored["failure_count"] += 1
            stored["last_error_code"] = error_code[:120]
            stored["processing_status"] = (
                "failed" if stored["failure_count"] >= 2 else "published"
            )
            return True

    def get_processing_status(self, event_id: str) -> str | None:
        with self._lock:
            stored = self._events.get(event_id)
            return str(stored["processing_status"]) if stored else None


class PostgresSharePointWebhookRepository(SharePointWebhookRepository):
    def __init__(self, connect: Callable[..., Any] | None = None) -> None:
        self._connect = connect

    def store_batch(
        self, events: list[SharePointChangeNotification]
    ) -> StoreBatchResult:
        connection = self._connection()
        created = 0
        duplicates = 0
        try:
            with connection.cursor() as cursor:
                for event in events:
                    payload = sanitized_payload(event)
                    payload_hash = hash_payload(payload)
                    cursor.execute(
                        """
                        INSERT INTO public.sharepoint_webhook_events (
                            event_id, subscription_id, change_type, resource,
                            site_id, list_id, item_id, partner_source_id,
                            occurred_at, payload_hash, payload
                        ) VALUES (
                            %s::uuid, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s::jsonb
                        )
                        ON CONFLICT (event_id) DO NOTHING
                        RETURNING event_id;
                        """,
                        (
                            str(event.event_id),
                            event.subscription_id,
                            event.change_type.value,
                            event.resource,
                            event.resource_data.site_id,
                            event.resource_data.list_id,
                            event.resource_data.item_id,
                            event.resource_data.partner_source_id,
                            event.occurred_at,
                            payload_hash,
                            _json(payload),
                        ),
                    )
                    if cursor.fetchone() is not None:
                        created += 1
                        continue
                    cursor.execute(
                        """
                        SELECT payload_hash
                        FROM public.sharepoint_webhook_events
                        WHERE event_id = %s::uuid;
                        """,
                        (str(event.event_id),),
                    )
                    existing = cursor.fetchone()
                    if existing is None or str(existing[0]) != payload_hash:
                        raise SharePointWebhookConflictError(
                            "eventId pertence a outra notificação."
                        )
                    duplicates += 1
            connection.commit()
            return StoreBatchResult(len(events), created, duplicates)
        except SharePointWebhookConflictError:
            connection.rollback()
            raise
        except Exception as error:
            connection.rollback()
            raise SharePointWebhookStorageError(
                "Não foi possível persistir a notificação."
            ) from error
        finally:
            connection.close()

    def get_payload(self, event_id: str) -> dict[str, Any] | None:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT payload
                    FROM public.sharepoint_webhook_events
                    WHERE event_id = %s::uuid;
                    """,
                    (event_id,),
                )
                row = cursor.fetchone()
                return dict(row[0]) if row else None
        except Exception as error:
            raise SharePointWebhookStorageError(
                "Não foi possível consultar a notificação."
            ) from error
        finally:
            connection.close()

    def list_pending(self, limit: int = 100) -> list[PendingSharePointEvent]:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT event_id::text, payload
                    FROM public.sharepoint_webhook_events
                    WHERE processing_status = 'pending'
                    ORDER BY received_at, event_id
                    LIMIT %s;
                    """,
                    (_bounded_limit(limit),),
                )
                return [
                    PendingSharePointEvent(str(row[0]), dict(row[1]))
                    for row in cursor.fetchall()
                ]
        except Exception as error:
            raise SharePointWebhookStorageError(
                "Não foi possível listar notificações pendentes."
            ) from error
        finally:
            connection.close()

    def mark_published(self, event_id: str) -> bool:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.sharepoint_webhook_events
                    SET processing_status = 'published', published_at = NOW()
                    WHERE event_id = %s::uuid
                      AND processing_status = 'pending'
                    RETURNING event_id;
                    """,
                    (event_id,),
                )
                changed = cursor.fetchone() is not None
            connection.commit()
            return changed
        except Exception as error:
            connection.rollback()
            raise SharePointWebhookStorageError(
                "Não foi possível confirmar a publicação da notificação."
            ) from error
        finally:
            connection.close()

    def claim_for_processing(self, event_id: str) -> bool:
        return self._transition(
            event_id,
            from_status="published",
            to_status="processing",
        )

    def mark_processed(self, event_id: str) -> bool:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.sharepoint_webhook_events
                    SET processing_status = 'processed', processed_at = NOW(),
                        last_error_code = NULL
                    WHERE event_id = %s::uuid
                      AND processing_status = 'processing'
                    RETURNING event_id;
                    """,
                    (event_id,),
                )
                changed = cursor.fetchone() is not None
            connection.commit()
            return changed
        except Exception as error:
            connection.rollback()
            raise SharePointWebhookStorageError(
                "Não foi possível concluir a notificação."
            ) from error
        finally:
            connection.close()

    def mark_processing_failed(self, event_id: str, error_code: str) -> bool:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.sharepoint_webhook_events
                    SET failure_count = failure_count + 1,
                        processing_status = CASE
                            WHEN failure_count + 1 >= 2 THEN 'failed'
                            ELSE 'published'
                        END,
                        last_error_code = %s
                    WHERE event_id = %s::uuid
                      AND processing_status = 'processing'
                    RETURNING event_id;
                    """,
                    (error_code[:120], event_id),
                )
                changed = cursor.fetchone() is not None
            connection.commit()
            return changed
        except Exception as error:
            connection.rollback()
            raise SharePointWebhookStorageError(
                "Não foi possível registrar a falha de processamento."
            ) from error
        finally:
            connection.close()

    def get_processing_status(self, event_id: str) -> str | None:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT processing_status
                    FROM public.sharepoint_webhook_events
                    WHERE event_id = %s::uuid;
                    """,
                    (event_id,),
                )
                row = cursor.fetchone()
                return str(row[0]) if row else None
        except Exception as error:
            raise SharePointWebhookStorageError(
                "Não foi possível consultar o estado da notificação."
            ) from error
        finally:
            connection.close()

    def _transition(
        self,
        event_id: str,
        *,
        from_status: str,
        to_status: str,
    ) -> bool:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.sharepoint_webhook_events
                    SET processing_status = %s
                    WHERE event_id = %s::uuid
                      AND processing_status = %s
                    RETURNING event_id;
                    """,
                    (to_status, event_id, from_status),
                )
                changed = cursor.fetchone() is not None
            connection.commit()
            return changed
        except Exception as error:
            connection.rollback()
            raise SharePointWebhookStorageError(
                "Não foi possível alterar o estado da notificação."
            ) from error
        finally:
            connection.close()

    def _connection(self) -> Any:
        try:
            return open_database_connection(connect=self._connect)
        except Exception as error:
            raise SharePointWebhookStorageError(
                "Não foi possível conectar à inbox de notificações."
            ) from error


def sanitized_payload(event: SharePointChangeNotification) -> dict[str, Any]:
    """Serializa somente dados de negócio; `clientState` nunca é persistido."""

    return {
        "eventId": str(event.event_id),
        "subscriptionId": event.subscription_id,
        "changeType": event.change_type.value,
        "resource": event.resource,
        "resourceData": event.resource_data.model_dump(mode="json", by_alias=True),
        "occurredAt": event.occurred_at.isoformat(),
    }


def hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def get_sharepoint_webhook_repository() -> SharePointWebhookRepository:
    mode = os.getenv("SHAREPOINT_WEBHOOK_REPOSITORY_MODE", "database").strip().lower()
    if mode == "memory":
        return InMemorySharePointWebhookRepository()
    if mode == "database":
        return PostgresSharePointWebhookRepository()
    raise SharePointWebhookStorageError("Modo de persistência inválido.")


def reset_sharepoint_webhook_repository() -> None:
    get_sharepoint_webhook_repository.cache_clear()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _bounded_limit(limit: int) -> int:
    return min(max(limit, 1), 1_000)
