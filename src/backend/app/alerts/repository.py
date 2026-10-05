"""Persistencia e garantias idempotentes do fluxo de alertas."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from threading import RLock
from typing import Any

from app.alerts.errors import (
    AlertConfigurationError,
    AlertConflictError,
    AlertNotFoundError,
    NotificationNotFoundError,
)
from app.alerts.schemas import (
    AlertEvaluation,
    AlertNotification,
    AlertSubscription,
    AlertWorkflowSession,
    NotificationDeliveryCallbackRequest,
    NotificationDeliveryCallbackResponse,
    NotificationStatus,
)
from app.database.connection import open_database_connection


class AlertRepository(ABC):
    @abstractmethod
    def create_subscription(self, value: AlertSubscription) -> tuple[AlertSubscription, bool]: ...
    @abstractmethod
    def get_subscription(self, subscription_id: str) -> AlertSubscription: ...
    @abstractmethod
    def list_subscriptions(self, owner: str) -> list[AlertSubscription]: ...
    @abstractmethod
    def save_subscription(self, value: AlertSubscription, previous_revision: int) -> AlertSubscription: ...
    @abstractmethod
    def enqueue_and_save_subscription(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        value: AlertSubscription,
        previous_revision: int,
    ) -> AlertSubscription: ...
    @abstractmethod
    def due_subscriptions(self, now: datetime, limit: int) -> list[AlertSubscription]: ...
    @abstractmethod
    def save_evaluation(self, value: AlertEvaluation) -> None: ...
    @abstractmethod
    def create_notification(self, value: AlertNotification, episode_key: str) -> bool: ...
    @abstractmethod
    def list_notifications(self, recipient: str) -> list[AlertNotification]: ...
    @abstractmethod
    def mark_read(self, notification_id: str, recipient: str, read_at: datetime) -> AlertNotification: ...
    @abstractmethod
    def save_delivery_callback(
        self,
        value: NotificationDeliveryCallbackResponse,
        payload_hash: str,
        callback_payload: dict[str, Any],
        event_id: str,
    ) -> NotificationDeliveryCallbackResponse: ...
    @abstractmethod
    def record_delivery_attempt(
        self, callback: NotificationDeliveryCallbackRequest
    ) -> bool: ...
    @abstractmethod
    def enqueue(self, event_id: str, event_type: str, correlation_id: str, payload: dict[str, Any]) -> None: ...
    @abstractmethod
    def create_workflow(self, value: AlertWorkflowSession) -> None: ...
    @abstractmethod
    def get_workflow(self, session_id: str) -> AlertWorkflowSession: ...
    @abstractmethod
    def save_workflow(self, value: AlertWorkflowSession, previous_revision: int) -> AlertWorkflowSession: ...


class InMemoryAlertRepository(AlertRepository):
    def __init__(self) -> None:
        self._subscriptions: dict[str, AlertSubscription] = {}
        self._idempotency: dict[tuple[str, str], str] = {}
        self._notifications: dict[str, AlertNotification] = {}
        self._episodes: set[str] = set()
        self._evaluations: dict[str, AlertEvaluation] = {}
        self._workflows: dict[str, AlertWorkflowSession] = {}
        self.delivery_callbacks: dict[str, dict[str, Any]] = {}
        self.delivery_attempts: list[dict[str, Any]] = []
        self.outbox: list[dict[str, Any]] = []
        self._lock = RLock()

    def create_subscription(self, value: AlertSubscription) -> tuple[AlertSubscription, bool]:
        with self._lock:
            key = (value.owner_subject, value.idempotency_key)
            existing = self._idempotency.get(key)
            if existing:
                return deepcopy(self._subscriptions[existing]), False
            self._subscriptions[value.subscription_id] = deepcopy(value)
            self._idempotency[key] = value.subscription_id
            return deepcopy(value), True

    def get_subscription(self, subscription_id: str) -> AlertSubscription:
        with self._lock:
            value = self._subscriptions.get(subscription_id)
            if value is None:
                raise AlertNotFoundError()
            return deepcopy(value)

    def list_subscriptions(self, owner: str) -> list[AlertSubscription]:
        with self._lock:
            return [deepcopy(item) for item in self._subscriptions.values() if item.owner_subject == owner]

    def save_subscription(self, value: AlertSubscription, previous_revision: int) -> AlertSubscription:
        with self._lock:
            current = self._subscriptions.get(value.subscription_id)
            if current is None:
                raise AlertNotFoundError()
            if current.revision != previous_revision:
                raise AlertConflictError("A inscricao foi atualizada em outra solicitacao.")
            self._subscriptions[value.subscription_id] = deepcopy(value)
            return deepcopy(value)

    def enqueue_and_save_subscription(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        value: AlertSubscription,
        previous_revision: int,
    ) -> AlertSubscription:
        with self._lock:
            current = self._subscriptions.get(value.subscription_id)
            if current is None:
                raise AlertNotFoundError()
            if current.revision != previous_revision:
                raise AlertConflictError("A inscricao foi atualizada em outra solicitacao.")
            if not any(item["event_id"] == event_id for item in self.outbox):
                self.outbox.append({"event_id": event_id, "event_type": event_type, "correlation_id": value.correlation_id, "payload": deepcopy(payload)})
            self._subscriptions[value.subscription_id] = deepcopy(value)
            return deepcopy(value)

    def due_subscriptions(self, now: datetime, limit: int) -> list[AlertSubscription]:
        with self._lock:
            values = [item for item in self._subscriptions.values() if item.status.value == "active" and item.next_evaluation_at <= now]
            return [deepcopy(item) for item in sorted(values, key=lambda item: item.next_evaluation_at)[:limit]]

    def save_evaluation(self, value: AlertEvaluation) -> None:
        with self._lock:
            self._evaluations[value.evaluation_id] = deepcopy(value)

    def create_notification(self, value: AlertNotification, episode_key: str) -> bool:
        with self._lock:
            if episode_key in self._episodes:
                return False
            self._episodes.add(episode_key)
            self._notifications[value.notification_id] = deepcopy(value)
            return True

    def list_notifications(self, recipient: str) -> list[AlertNotification]:
        with self._lock:
            values = [item for item in self._notifications.values() if item.recipient_subject == recipient]
            return [deepcopy(item) for item in sorted(values, key=lambda item: item.created_at, reverse=True)]

    def mark_read(self, notification_id: str, recipient: str, read_at: datetime) -> AlertNotification:
        with self._lock:
            item = self._notifications.get(notification_id)
            if item is None or item.recipient_subject != recipient:
                raise AlertNotFoundError()
            item.status = NotificationStatus.READ
            item.read_at = read_at
            return deepcopy(item)

    def save_delivery_callback(
        self,
        value: NotificationDeliveryCallbackResponse,
        payload_hash: str,
        callback_payload: dict[str, Any],
        event_id: str,
    ) -> NotificationDeliveryCallbackResponse:
        with self._lock:
            notification_id = str(value.notification_id)
            if notification_id not in self._notifications:
                raise NotificationNotFoundError()
            existing = self.delivery_callbacks.get(value.callback_id)
            if existing is not None:
                if not hmac.compare_digest(existing["payload_hash"], payload_hash):
                    raise AlertConflictError(
                        "O identificador do callback pertence a outro retorno."
                    )
                return deepcopy(existing["value"])
            self.delivery_callbacks[value.callback_id] = {
                "payload_hash": payload_hash,
                "callback_payload": deepcopy(callback_payload),
                "value": deepcopy(value),
            }
            notification = self._notifications[notification_id]
            self.outbox.append(
                {
                    "event_id": event_id,
                    "event_type": "notification.delivery.received",
                    "correlation_id": notification.correlation_id,
                    "payload": deepcopy(callback_payload),
                }
            )
            return deepcopy(value)

    def record_delivery_attempt(
        self, callback: NotificationDeliveryCallbackRequest
    ) -> bool:
        with self._lock:
            notification_id = str(callback.notification_id)
            if notification_id not in self._notifications:
                raise NotificationNotFoundError()
            persisted = self.delivery_callbacks.get(callback.callback_id)
            if (
                persisted is None
                or str(persisted["value"].notification_id) != notification_id
                or not hmac.compare_digest(
                    persisted["payload_hash"], _delivery_payload_hash(callback)
                )
            ):
                raise AlertConflictError(
                    "O callback do evento nao corresponde ao retorno persistido."
                )
            if any(
                item["callback_id"] == callback.callback_id
                for item in self.delivery_attempts
            ):
                return False
            attempt_number = 1 + max(
                (
                    item["attempt_number"]
                    for item in self.delivery_attempts
                    if item["notification_id"] == notification_id
                ),
                default=0,
            )
            self.delivery_attempts.append(
                {
                    "notification_id": notification_id,
                    "callback_id": callback.callback_id,
                    "channel": callback.provider,
                    "attempt_number": attempt_number,
                    "status": (
                        "available"
                        if callback.status.value == "delivered"
                        else "failed"
                    ),
                    "error_code": callback.error_code,
                    "attempted_at": callback.attempted_at,
                }
            )
            return True

    def enqueue(self, event_id: str, event_type: str, correlation_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            if any(item["event_id"] == event_id for item in self.outbox):
                return
            self.outbox.append({"event_id": event_id, "event_type": event_type, "correlation_id": correlation_id, "payload": deepcopy(payload)})

    def create_workflow(self, value: AlertWorkflowSession) -> None:
        with self._lock:
            self._workflows[value.session_id] = deepcopy(value)

    def get_workflow(self, session_id: str) -> AlertWorkflowSession:
        with self._lock:
            value = self._workflows.get(session_id)
            if value is None:
                raise AlertNotFoundError()
            return deepcopy(value)

    def save_workflow(self, value: AlertWorkflowSession, previous_revision: int) -> AlertWorkflowSession:
        with self._lock:
            current = self._workflows.get(value.session_id)
            if current is None:
                raise AlertNotFoundError()
            if current.revision != previous_revision:
                raise AlertConflictError("O workflow foi atualizado em outra solicitacao.")
            self._workflows[value.session_id] = deepcopy(value)
            return deepcopy(value)


class PostgresAlertRepository(AlertRepository):
    def _connection(self) -> Any:
        try:
            return open_database_connection()
        except Exception as error:
            raise AlertConfigurationError() from error

    def create_subscription(self, value: AlertSubscription) -> tuple[AlertSubscription, bool]:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT subscription_payload FROM public.alert_subscriptions WHERE owner_subject=%s AND idempotency_key=%s", (value.owner_subject, value.idempotency_key))
                row = cursor.fetchone()
                if row:
                    return AlertSubscription.model_validate(row[0]), False
                cursor.execute("""INSERT INTO public.alert_subscriptions
                    (subscription_id, owner_subject, project_id, status, next_evaluation_at, revision, idempotency_key, correlation_id, subscription_payload, created_at, updated_at)
                    VALUES (%s::uuid,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s)""",
                    (value.subscription_id,value.owner_subject,value.rule.project_id,value.status.value,value.next_evaluation_at,value.revision,value.idempotency_key,value.correlation_id,_json(value),value.created_at,value.updated_at))
                self._audit(cursor, "alert.subscription.created", value.correlation_id, {"subscription_id": value.subscription_id}, "alert_workflow")
            connection.commit()
            return value, True
        except Exception as error:
            connection.rollback()
            if getattr(error, "sqlstate", None) == "23505":
                raise AlertConflictError("Chave de idempotencia ja utilizada.") from error
            raise AlertConfigurationError() from error
        finally:
            connection.close()

    def get_subscription(self, subscription_id: str) -> AlertSubscription:
        return self._one("SELECT subscription_payload FROM public.alert_subscriptions WHERE subscription_id=%s::uuid", (subscription_id,), AlertSubscription)

    def list_subscriptions(self, owner: str) -> list[AlertSubscription]:
        return self._many("SELECT subscription_payload FROM public.alert_subscriptions WHERE owner_subject=%s ORDER BY created_at DESC", (owner,), AlertSubscription)

    def save_subscription(self, value: AlertSubscription, previous_revision: int) -> AlertSubscription:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""UPDATE public.alert_subscriptions SET status=%s,next_evaluation_at=%s,revision=%s,subscription_payload=%s::jsonb,updated_at=%s
                    WHERE subscription_id=%s::uuid AND revision=%s""", (value.status.value,value.next_evaluation_at,value.revision,_json(value),value.updated_at,value.subscription_id,previous_revision))
                if cursor.rowcount == 0:
                    raise AlertConflictError("A inscricao foi atualizada em outra solicitacao.")
            connection.commit()
            return value
        except AlertConflictError:
            connection.rollback(); raise
        except Exception as error:
            connection.rollback(); raise AlertConfigurationError() from error
        finally:
            connection.close()

    def enqueue_and_save_subscription(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        value: AlertSubscription,
        previous_revision: int,
    ) -> AlertSubscription:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""UPDATE public.alert_subscriptions SET status=%s,next_evaluation_at=%s,revision=%s,subscription_payload=%s::jsonb,updated_at=%s
                    WHERE subscription_id=%s::uuid AND revision=%s""", (value.status.value,value.next_evaluation_at,value.revision,_json(value),value.updated_at,value.subscription_id,previous_revision))
                if cursor.rowcount == 0:
                    raise AlertConflictError("A inscricao foi atualizada em outra solicitacao.")
                cursor.execute("""INSERT INTO public.message_outbox (event_id,event_type,correlation_id,payload) VALUES (%s::uuid,%s,%s,%s::jsonb) ON CONFLICT (event_id) DO NOTHING""", (event_id,event_type,value.correlation_id,json.dumps(payload,default=str)))
            connection.commit()
            return value
        except AlertConflictError:
            connection.rollback(); raise
        except Exception as error:
            connection.rollback(); raise AlertConfigurationError() from error
        finally:
            connection.close()

    def due_subscriptions(self, now: datetime, limit: int) -> list[AlertSubscription]:
        return self._many("SELECT subscription_payload FROM public.alert_subscriptions WHERE status='active' AND next_evaluation_at<=%s ORDER BY next_evaluation_at LIMIT %s", (now, limit), AlertSubscription)

    def save_evaluation(self, value: AlertEvaluation) -> None:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""INSERT INTO public.alert_evaluations (evaluation_id,subscription_id,correlation_id,as_of_date,outcome,snapshot_hash,evaluation_payload,created_at,completed_at)
                    VALUES (%s::uuid,%s::uuid,%s,%s,%s,%s,%s::jsonb,%s,%s) ON CONFLICT (evaluation_id) DO NOTHING""",
                    (value.evaluation_id,value.subscription_id,value.correlation_id,value.as_of_date,value.outcome.value,value.snapshot_hash,_json(value),value.created_at,value.completed_at))
                if cursor.rowcount:
                    self._audit(cursor,"alert.evaluation.completed",value.correlation_id,{"evaluation_id":value.evaluation_id,"outcome":value.outcome.value},"alert_evaluator")
            connection.commit()
        except Exception as error:
            connection.rollback(); raise AlertConfigurationError() from error
        finally:
            connection.close()

    def create_notification(self, value: AlertNotification, episode_key: str) -> bool:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""INSERT INTO public.alert_occurrences (occurrence_id,subscription_id,item_id,episode_key,first_detected_at,last_seen_at,state)
                    VALUES (%s::uuid,%s::uuid,%s,%s,%s,%s,'open') ON CONFLICT (episode_key) DO NOTHING""",
                    (value.occurrence_id,value.subscription_id,value.item_id,episode_key,value.created_at,value.created_at))
                if cursor.rowcount == 0:
                    connection.rollback(); return False
                cursor.execute("""INSERT INTO public.alert_notifications (notification_id,occurrence_id,subscription_id,recipient_subject,status,notification_payload,created_at)
                    VALUES (%s::uuid,%s::uuid,%s::uuid,%s,%s,%s::jsonb,%s)""", (value.notification_id,value.occurrence_id,value.subscription_id,value.recipient_subject,value.status.value,_json(value),value.created_at))
                cursor.execute("""INSERT INTO public.notification_delivery_attempts (notification_id,attempt_number,status)
                    VALUES (%s::uuid,1,'available')""", (value.notification_id,))
                self._audit(cursor,"alert.notification.available",value.correlation_id,{"notification_id":value.notification_id},"notification_dispatcher")
            connection.commit(); return True
        except Exception as error:
            connection.rollback(); raise AlertConfigurationError() from error
        finally:
            connection.close()

    def list_notifications(self, recipient: str) -> list[AlertNotification]:
        return self._many("SELECT notification_payload FROM public.alert_notifications WHERE recipient_subject=%s ORDER BY created_at DESC LIMIT 200", (recipient,), AlertNotification)

    def mark_read(self, notification_id: str, recipient: str, read_at: datetime) -> AlertNotification:
        value = self._one("SELECT notification_payload FROM public.alert_notifications WHERE notification_id=%s::uuid AND recipient_subject=%s", (notification_id, recipient), AlertNotification)
        value.status = NotificationStatus.READ; value.read_at = read_at
        self._execute("UPDATE public.alert_notifications SET status='read',read_at=%s,notification_payload=%s::jsonb WHERE notification_id=%s::uuid", (read_at,_json(value),notification_id))
        return value

    def save_delivery_callback(
        self,
        value: NotificationDeliveryCallbackResponse,
        payload_hash: str,
        callback_payload: dict[str, Any],
        event_id: str,
    ) -> NotificationDeliveryCallbackResponse:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                # Serializa o mesmo callback_id entre requisicoes concorrentes.
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                    (value.callback_id,),
                )
                cursor.execute(
                    "SELECT notification_payload FROM public.alert_notifications "
                    "WHERE notification_id=%s::uuid FOR UPDATE",
                    (str(value.notification_id),),
                )
                notification_row = cursor.fetchone()
                if notification_row is None:
                    raise NotificationNotFoundError()
                row_notification = notification_row[0]
                cursor.execute(
                    "SELECT payload_hash,callback_payload,received_at "
                    "FROM public.notification_delivery_callbacks "
                    "WHERE callback_id=%s",
                    (value.callback_id,),
                )
                row = cursor.fetchone()
                if row is not None:
                    if not hmac.compare_digest(row[0], payload_hash):
                        raise AlertConflictError(
                            "O identificador do callback pertence a outro retorno."
                        )
                    stored = dict(row[1])
                    stored["received_at"] = row[2]
                    return NotificationDeliveryCallbackResponse.model_validate(stored)
                cursor.execute(
                    """INSERT INTO public.notification_delivery_callbacks
                    (callback_id,notification_id,payload_hash,callback_payload,received_at)
                    VALUES (%s,%s::uuid,%s,%s::jsonb,%s)""",
                    (
                        value.callback_id,
                        str(value.notification_id),
                        payload_hash,
                        json.dumps(callback_payload, ensure_ascii=False),
                        value.received_at,
                    ),
                )
                cursor.execute(
                    """INSERT INTO public.message_outbox
                    (event_id,event_type,correlation_id,payload)
                    VALUES (%s::uuid,'notification.delivery.received',%s,%s::jsonb)""",
                    (
                        event_id,
                        str(row_notification["correlation_id"]),
                        json.dumps(callback_payload, ensure_ascii=False),
                    ),
                )
            connection.commit()
            return value
        except (AlertConflictError, NotificationNotFoundError):
            connection.rollback()
            raise
        except Exception as error:
            connection.rollback()
            raise AlertConfigurationError() from error
        finally:
            connection.close()

    def record_delivery_attempt(
        self, callback: NotificationDeliveryCallbackRequest
    ) -> bool:
        connection = self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM public.alert_notifications "
                    "WHERE notification_id=%s::uuid FOR UPDATE",
                    (str(callback.notification_id),),
                )
                if cursor.fetchone() is None:
                    raise NotificationNotFoundError()
                cursor.execute(
                    "SELECT payload_hash FROM public.notification_delivery_callbacks "
                    "WHERE callback_id=%s AND notification_id=%s::uuid",
                    (callback.callback_id, str(callback.notification_id)),
                )
                callback_row = cursor.fetchone()
                if callback_row is None or not hmac.compare_digest(
                    callback_row[0], _delivery_payload_hash(callback)
                ):
                    raise AlertConflictError(
                        "O callback do evento nao corresponde ao retorno persistido."
                    )
                cursor.execute(
                    "SELECT COALESCE(MAX(attempt_number),0)+1 "
                    "FROM public.notification_delivery_attempts "
                    "WHERE notification_id=%s::uuid",
                    (str(callback.notification_id),),
                )
                attempt_number = cursor.fetchone()[0]
                cursor.execute(
                    """INSERT INTO public.notification_delivery_attempts
                    (notification_id,callback_id,channel,attempt_number,status,error_code,attempted_at)
                    VALUES (%s::uuid,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING""",
                    (
                        str(callback.notification_id),
                        callback.callback_id,
                        callback.provider,
                        attempt_number,
                        "available" if callback.status.value == "delivered" else "failed",
                        callback.error_code,
                        callback.attempted_at,
                    ),
                )
                created = cursor.rowcount > 0
            connection.commit()
            return created
        except (AlertConflictError, NotificationNotFoundError):
            connection.rollback()
            raise
        except Exception as error:
            connection.rollback()
            raise AlertConfigurationError() from error
        finally:
            connection.close()

    def enqueue(self, event_id: str, event_type: str, correlation_id: str, payload: dict[str, Any]) -> None:
        self._execute("""INSERT INTO public.message_outbox (event_id,event_type,correlation_id,payload) VALUES (%s::uuid,%s,%s,%s::jsonb) ON CONFLICT (event_id) DO NOTHING""", (event_id,event_type,correlation_id,json.dumps(payload,default=str)))

    def create_workflow(self, value: AlertWorkflowSession) -> None:
        self._execute("""INSERT INTO public.workflow_sessions (session_id,workflow_name,requested_by,conversation_id,interaction_id,correlation_id,workflow_status,current_step,revision,session_payload,created_at,updated_at)
            VALUES (%s::uuid,'alerta_prazo_atraso',%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s)""", (value.session_id,value.requested_by,value.conversation_id,value.interaction_id,value.correlation_id,value.status.value,value.current_step.value,value.revision,_json(value),value.created_at,value.updated_at))

    def get_workflow(self, session_id: str) -> AlertWorkflowSession:
        return self._one("SELECT session_payload FROM public.workflow_sessions WHERE session_id=%s::uuid AND workflow_name='alerta_prazo_atraso'", (session_id,), AlertWorkflowSession)

    def save_workflow(self, value: AlertWorkflowSession, previous_revision: int) -> AlertWorkflowSession:
        connection=self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""UPDATE public.workflow_sessions SET workflow_status=%s,current_step=%s,revision=%s,session_payload=%s::jsonb,updated_at=%s WHERE session_id=%s::uuid AND revision=%s""", (value.status.value,value.current_step.value,value.revision,_json(value),value.updated_at,value.session_id,previous_revision))
                if cursor.rowcount==0: raise AlertConflictError("O workflow foi atualizado em outra solicitacao.")
            connection.commit(); return value
        except AlertConflictError:
            connection.rollback(); raise
        except Exception as error:
            connection.rollback(); raise AlertConfigurationError() from error
        finally: connection.close()

    def _one(self, query: str, params: tuple[Any, ...], model: Any) -> Any:
        values=self._many(query,params,model)
        if not values: raise AlertNotFoundError()
        return values[0]

    def _many(self, query: str, params: tuple[Any, ...], model: Any) -> list[Any]:
        connection=self._connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query,params); return [model.model_validate(row[0]) for row in cursor.fetchall()]
        except AlertNotFoundError: raise
        except Exception as error: raise AlertConfigurationError() from error
        finally: connection.close()

    def _execute(self, query: str, params: tuple[Any, ...]) -> None:
        connection=self._connection()
        try:
            with connection.cursor() as cursor: cursor.execute(query,params)
            connection.commit()
        except Exception as error:
            connection.rollback(); raise AlertConfigurationError() from error
        finally: connection.close()

    @staticmethod
    def _audit(cursor: Any, event_type: str, correlation_id: str, payload: dict[str, Any], component: str) -> None:
        cursor.execute(
            """
            INSERT INTO public.audit_events (
                event_type, component, event_status, event_payload,
                correlation_id, user_id
            ) VALUES (
                %s, %s, 'sucesso', %s::jsonb, %s,
                (SELECT u.id
                   FROM public.users u
                   JOIN public.alert_subscriptions s
                     ON s.owner_subject = u.entra_object_id
                  WHERE s.correlation_id = %s AND u.is_active = TRUE
                  LIMIT 1)
            )
            """,
            (event_type, component, json.dumps(payload), correlation_id, correlation_id),
        )


@lru_cache(maxsize=1)
def get_alert_repository() -> AlertRepository:
    mode=os.getenv("ALERT_REPOSITORY_MODE","memory").strip().lower()
    if mode=="memory": return InMemoryAlertRepository()
    if mode=="database": return PostgresAlertRepository()
    raise AlertConfigurationError("ALERT_REPOSITORY_MODE invalido.")


def reset_alert_repository() -> None:
    get_alert_repository.cache_clear()


def _json(value: Any) -> str:
    if hasattr(value,"model_dump"): value=value.model_dump(mode="json")
    return json.dumps(value,ensure_ascii=False,sort_keys=True,default=str)


def _delivery_payload_hash(callback: NotificationDeliveryCallbackRequest) -> str:
    payload = callback.model_dump(mode="json")
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
