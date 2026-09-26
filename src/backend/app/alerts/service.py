"""Regras, agendamento, avaliacao e notificacao de prazo."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.alerts.errors import AlertAccessDeniedError, AlertConflictError, AlertConfigurationError
from app.alerts.repository import AlertRepository, get_alert_repository
from app.alerts.schemas import (
    AlertEvaluation,
    AlertNotification,
    AlertSubscription,
    AlertSubscriptionResponse,
    ChangeSubscriptionRequest,
    CreateAlertRequest,
    EvaluationOutcome,
    NotificationListResponse,
    NotificationDeliveryCallbackRequest,
    NotificationDeliveryCallbackResponse,
    NotificationStatus,
    PrepareAlertRequest,
    PrepareAlertResponse,
    PreparedAlert,
    ScheduleItem,
    SubscriptionStatus,
    TriggerType,
)
from app.alerts.source import ScheduleSource, get_schedule_source
from app.reports.schemas import ReportScope, ScopeType
from app.reports.security import (
    ReportIdentity,
    authorize_scope,
    resolve_report_identity_by_subject,
)


class AlertService:
    def __init__(self, repository: AlertRepository, source: ScheduleSource, secret: bytes | None = None) -> None:
        self.repository = repository
        self.source = source
        self.secret = secret

    def prepare(self, request: PrepareAlertRequest, identity: ReportIdentity) -> PrepareAlertResponse:
        authorize_scope(identity, ReportScope(type=ScopeType.PROJECT, id=request.rule.project_id))
        now = _now()
        prepared = PreparedAlert(
            request=request,
            requested_by=identity.subject,
            correlation_id=str(uuid4()),
            prepared_at=now,
            expires_at=now + timedelta(minutes=15),
        )
        summary = (
            f"Verificar {request.rule.project_label} {request.rule.trigger_type.value} "
            f"e avisar quando um item ultrapassar {request.rule.threshold_days} dias corridos "
            f"de atraso. Canal: central interna; destinatario: {identity.display_name}."
        )
        return PrepareAlertResponse(
            confirmation_hash=self._signature(prepared),
            confirmation_summary=summary,
            prepared_alert=prepared,
        )

    def create(self, request: CreateAlertRequest, identity: ReportIdentity) -> tuple[AlertSubscription, bool]:
        prepared = request.prepared_alert
        if prepared.requested_by != identity.subject:
            raise AlertAccessDeniedError()
        if prepared.expires_at < _now():
            raise AlertConflictError("A confirmacao expirou; revise a configuracao.")
        if not hmac.compare_digest(request.confirmation_hash, self._signature(prepared)):
            raise AlertConflictError("A configuracao foi alterada apos a revisao.")
        authorize_scope(identity, ReportScope(type=ScopeType.PROJECT, id=prepared.request.rule.project_id))
        now = _now()
        subscription = AlertSubscription(
            subscription_id=str(uuid4()),
            correlation_id=prepared.correlation_id,
            idempotency_key=request.idempotency_key,
            owner_subject=identity.subject,
            rule=prepared.request.rule,
            next_evaluation_at=_next_run(now, prepared.request.rule),
            created_at=now,
            updated_at=now,
        )
        value, created = self.repository.create_subscription(subscription)
        # alert.subscription.created e um evento informativo registrado na auditoria
        # (ver PostgresAlertRepository.create_subscription). Nao e publicado no broker
        # porque nao possui fila consumidora vinculada; enfileira-lo geraria evento orfao.
        return value, created

    def get(self, subscription_id: str, identity: ReportIdentity) -> AlertSubscription:
        value = self.repository.get_subscription(subscription_id)
        self._authorize_owner(value, identity)
        return value

    def list(self, identity: ReportIdentity) -> list[AlertSubscription]:
        return self.repository.list_subscriptions(identity.subject)

    def change_status(self, subscription_id: str, target: SubscriptionStatus, request: ChangeSubscriptionRequest, identity: ReportIdentity) -> AlertSubscription:
        value = self.get(subscription_id, identity)
        if value.revision != request.revision:
            raise AlertConflictError("A revisao informada esta desatualizada.")
        if value.status == SubscriptionStatus.CANCELLED:
            if target == SubscriptionStatus.CANCELLED:
                return value
            raise AlertConflictError("Uma inscricao cancelada nao pode ser reativada.")
        previous = value.revision
        value.status = target
        value.revision += 1
        value.updated_at = _now()
        if target == SubscriptionStatus.ACTIVE:
            value.next_evaluation_at = _next_run(value.updated_at, value.rule)
        return self.repository.save_subscription(value, previous)

    def schedule_due(self, now: datetime | None = None, limit: int = 100) -> list[str]:
        current = now or _now()
        scheduled: list[str] = []
        for value in self.repository.due_subscriptions(current, min(max(limit, 1), 500)):
            event_id = str(uuid4())
            previous = value.revision
            value.next_evaluation_at = _next_run(current, value.rule)
            value.revision += 1
            value.updated_at = current
            self.repository.enqueue_and_save_subscription(
                event_id,
                "alert.evaluation.requested",
                {"subscription_id": value.subscription_id, "as_of": current.date().isoformat()},
                value,
                previous,
            )
            scheduled.append(value.subscription_id)
        return scheduled

    def evaluate(
        self,
        subscription_id: str,
        as_of: date | None = None,
        evaluation_id: str | None = None,
    ) -> AlertEvaluation:
        value = self.repository.get_subscription(subscription_id)
        if value.status != SubscriptionStatus.ACTIVE:
            raise AlertConflictError("A inscricao nao esta ativa.")
        try:
            worker_identity = resolve_report_identity_by_subject(value.owner_subject)
            authorize_scope(
                worker_identity,
                ReportScope(type=ScopeType.PROJECT, id=value.rule.project_id),
            )
        except Exception as error:
            previous = value.revision
            value.status = SubscriptionStatus.BLOCKED
            value.revision += 1
            value.updated_at = _now()
            self.repository.save_subscription(value, previous)
            raise AlertAccessDeniedError() from error
        reference = as_of or datetime.now(ZoneInfo(value.rule.timezone)).date()
        items = self.source.list_items(value.rule.project_id)
        details: list[dict] = []
        eligible: list[tuple[ScheduleItem, int]] = []
        indeterminate = False
        conclusive = False
        for item in items:
            if item.planned_end_date is None:
                indeterminate = True
                details.append({"item_id": item.item_id, "result": "missing_planned_date"})
                continue
            if _completed(item):
                conclusive = True
                details.append({"item_id": item.item_id, "result": "completed"})
                continue
            freshness_days = max(int(os.getenv("ALERT_DATA_FRESHNESS_DAYS", "45")), 1)
            if item.updated_at and (_now() - item.updated_at.astimezone(timezone.utc)).days > freshness_days:
                indeterminate = True
                details.append({"item_id": item.item_id, "result": "stale_data", "updated_at": item.updated_at.isoformat()})
                continue
            overdue = max((reference - item.planned_end_date).days, 0)
            matched = overdue > value.rule.threshold_days if value.rule.comparison_operator.value == "gt" else overdue >= value.rule.threshold_days
            conclusive = True
            details.append({"item_id": item.item_id, "overdue_days": overdue, "result": "matched" if matched else "not_matched", "source": item.source})
            if matched:
                eligible.append((item, overdue))
        if eligible:
            outcome = EvaluationOutcome.MATCHED
        elif indeterminate and not conclusive:
            outcome = EvaluationOutcome.INDETERMINATE
        else:
            outcome = EvaluationOutcome.NOT_MATCHED
        now = _now()
        snapshot = {"subscription_id": value.subscription_id, "as_of": reference.isoformat(), "details": details}
        evaluation = AlertEvaluation(
            evaluation_id=evaluation_id or str(uuid4()), subscription_id=value.subscription_id,
            correlation_id=value.correlation_id, as_of_date=reference, outcome=outcome,
            eligible_count=len(eligible), evaluated_count=len(items),
            snapshot_hash=hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest(),
            details=details, created_at=now, completed_at=_now(),
        )
        self.repository.save_evaluation(evaluation)
        for item, overdue in eligible:
            self._notify(value, item, overdue, reference)
        return evaluation

    def notifications(self, identity: ReportIdentity) -> NotificationListResponse:
        items = self.repository.list_notifications(identity.subject)
        return NotificationListResponse(items=items, unread_count=sum(item.status != NotificationStatus.READ for item in items))

    def mark_notification_read(self, notification_id: str, identity: ReportIdentity) -> AlertNotification:
        return self.repository.mark_read(notification_id, identity.subject, _now())

    def apply_delivery_callback(
        self, callback: NotificationDeliveryCallbackRequest
    ) -> NotificationDeliveryCallbackResponse:
        payload = callback.model_dump(mode="json")
        payload_hash = hashlib.sha256(
            json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        value = NotificationDeliveryCallbackResponse(
            **callback.model_dump(), received_at=_now()
        )
        return self.repository.save_delivery_callback(
            value, payload_hash, payload, str(uuid4())
        )

    def _notify(self, subscription: AlertSubscription, item: ScheduleItem, overdue: int, reference: date) -> None:
        # O bucket de reenvio e ancorado na virada do limiar (primeira notificacao = 0),
        # nao no total de dias de atraso, para respeitar o intervalo desde o primeiro alerta.
        days_since_threshold = max(overdue - subscription.rule.threshold_days, 0)
        repeat_bucket = (
            days_since_threshold // subscription.rule.resend_interval_days
            if subscription.rule.resend_interval_days
            else 0
        )
        episode_key = (
            f"{subscription.subscription_id}:{item.item_id}:"
            f"{item.planned_end_date.isoformat()}:{repeat_bucket}"
        )
        now = _now(); occurrence_id = str(uuid4())
        notification = AlertNotification(
            notification_id=str(uuid4()), correlation_id=subscription.correlation_id,
            subscription_id=subscription.subscription_id,
            occurrence_id=occurrence_id, recipient_subject=subscription.owner_subject,
            project_id=subscription.rule.project_id, item_id=item.item_id,
            title=f"Prazo atrasado: {item.description}",
            body=f"{item.description} esta {overdue} dias atrasada. Data de referencia: {reference.strftime('%d/%m/%Y')}.",
            reference_date=reference, overdue_days=overdue, created_at=now,
        )
        self.repository.enqueue(
            str(uuid4()),
            "alert.notification.requested",
            subscription.correlation_id,
            {
                "episode_key": episode_key,
                "notification": notification.model_dump(mode="json"),
            },
        )

    @staticmethod
    def _authorize_owner(value: AlertSubscription, identity: ReportIdentity) -> None:
        if value.owner_subject != identity.subject:
            raise AlertAccessDeniedError()

    def _signature(self, prepared: PreparedAlert) -> str:
        payload = prepared.model_dump_json(exclude_none=False).encode()
        return hmac.new(self.secret or _secret(), payload, hashlib.sha256).hexdigest()


def _completed(item: ScheduleItem) -> bool:
    return bool(item.completed_date or item.status in {"concluido", "cancelado"} or item.progress_percent == 100)


def _next_run(after: datetime, rule: object) -> datetime:
    zone = ZoneInfo(rule.timezone)
    local = after.astimezone(zone)
    candidate = local.replace(hour=rule.evaluation_time.hour, minute=rule.evaluation_time.minute, second=0, microsecond=0)
    if candidate <= local:
        candidate += timedelta(days=1)
    if rule.trigger_type == TriggerType.WEEKLY:
        while candidate.weekday() != rule.weekday:
            candidate += timedelta(days=1)
    return candidate.astimezone(timezone.utc)


def _secret() -> bytes:
    value = os.getenv("ALERT_CONFIRMATION_SECRET", "").strip()
    if not value:
        report_secret = os.getenv("REPORT_CONFIRMATION_SECRET", "").strip()
        if report_secret:
            return hmac.new(
                report_secret.encode(), b"alerta-prazo-atraso", hashlib.sha256
            ).digest()
    if not value:
        if os.getenv("ALERT_REPOSITORY_MODE", "memory") == "memory":
            value = "development-only-alert-secret"
        else:
            raise AlertConfigurationError("ALERT_CONFIRMATION_SECRET ausente.")
    return value.encode()


def _now() -> datetime:
    return datetime.now(timezone.utc)


@lru_cache(maxsize=1)
def get_alert_service() -> AlertService:
    return AlertService(get_alert_repository(), get_schedule_source())
