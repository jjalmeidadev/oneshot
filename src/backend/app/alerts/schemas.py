"""Contratos publicos e modelos persistidos do alerta de prazo."""

from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CONTRACT_VERSION = "1.0"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AlertDirective(StrictModel):
    kind: Literal["guided_workflow"] = "guided_workflow"
    action: Literal["start"] = "start"
    workflow: Literal["alerta_prazo_atraso"] = "alerta_prazo_atraso"
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    parameters: dict[str, Any] = Field(default_factory=dict)


class ComparisonOperator(str, Enum):
    GREATER_THAN = "gt"
    GREATER_OR_EQUAL = "gte"


class DayBasis(str, Enum):
    CALENDAR = "calendar_days"
    BUSINESS = "business_days"


class TriggerType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class EvaluationOutcome(str, Enum):
    MATCHED = "matched"
    NOT_MATCHED = "not_matched"
    INDETERMINATE = "indeterminate"
    FAILED = "failed"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    READ = "read"
    FAILED = "failed"


class DeliveryStatus(str, Enum):
    DELIVERED = "delivered"
    FAILED = "failed"


class AlertRule(StrictModel):
    project_id: str = Field(min_length=1, max_length=120)
    project_label: str = Field(min_length=1, max_length=220)
    threshold_days: int = Field(ge=0, le=3650)
    comparison_operator: ComparisonOperator = ComparisonOperator.GREATER_THAN
    day_basis: DayBasis = DayBasis.CALENDAR
    trigger_type: TriggerType = TriggerType.DAILY
    evaluation_time: time = time(8, 0)
    weekday: int | None = Field(default=None, ge=0, le=6)
    timezone: str = Field(default="America/Sao_Paulo", min_length=1, max_length=80)
    resend_interval_days: int | None = Field(default=None, ge=1, le=365)

    @model_validator(mode="after")
    def validate_schedule(self) -> "AlertRule":
        if self.trigger_type == TriggerType.WEEKLY and self.weekday is None:
            raise ValueError("Alertas semanais exigem o dia da semana")
        if self.day_basis == DayBasis.BUSINESS:
            raise ValueError("Dias uteis exigem calendario corporativo configurado")
        return self


class PrepareAlertRequest(StrictModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    conversation_id: str = Field(min_length=1, max_length=160)
    interaction_id: str | None = Field(default=None, max_length=160)
    rule: AlertRule


class PreparedAlert(StrictModel):
    request: PrepareAlertRequest
    requested_by: str
    correlation_id: str
    prepared_at: datetime
    expires_at: datetime


class PrepareAlertResponse(StrictModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    confirmation_hash: str
    confirmation_summary: str
    prepared_alert: PreparedAlert
    warnings: list[str] = Field(default_factory=list)


class CreateAlertRequest(StrictModel):
    prepared_alert: PreparedAlert
    confirmation_hash: str = Field(min_length=64, max_length=64)
    idempotency_key: str = Field(min_length=8, max_length=160)


class AlertSubscription(StrictModel):
    subscription_id: str
    correlation_id: str
    idempotency_key: str
    owner_subject: str
    rule: AlertRule
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    revision: int = 0
    next_evaluation_at: datetime
    created_at: datetime
    updated_at: datetime


class AlertSubscriptionResponse(StrictModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    subscription: AlertSubscription


class ChangeSubscriptionRequest(StrictModel):
    revision: int = Field(ge=0)
    client_action_id: str = Field(min_length=8, max_length=160)


class ScheduleItem(StrictModel):
    item_id: str
    project_id: str
    description: str
    planned_end_date: date | None
    completed_date: date | None = None
    progress_percent: float | None = Field(default=None, ge=0, le=100)
    status: str | None = None
    updated_at: datetime | None = None
    source: str


class AlertEvaluation(StrictModel):
    evaluation_id: str
    subscription_id: str
    correlation_id: str
    as_of_date: date
    outcome: EvaluationOutcome
    eligible_count: int = 0
    evaluated_count: int = 0
    snapshot_hash: str
    details: list[dict[str, Any]] = Field(default_factory=list)
    error_code: str | None = None
    created_at: datetime
    completed_at: datetime


class AlertNotification(StrictModel):
    notification_id: str
    correlation_id: str
    subscription_id: str
    occurrence_id: str
    recipient_subject: str
    project_id: str
    item_id: str
    title: str
    body: str
    reference_date: date
    overdue_days: int
    status: NotificationStatus = NotificationStatus.AVAILABLE
    created_at: datetime
    read_at: datetime | None = None


class NotificationListResponse(StrictModel):
    items: list[AlertNotification]
    unread_count: int


class NotificationDeliveryCallbackRequest(StrictModel):
    callback_id: str = Field(min_length=8, max_length=160)
    notification_id: UUID
    provider: str = Field(min_length=1, max_length=80)
    status: DeliveryStatus
    attempted_at: datetime
    error_code: str | None = Field(default=None, min_length=1, max_length=120)


class NotificationDeliveryCallbackResponse(NotificationDeliveryCallbackRequest):
    received_at: datetime


class NotificationDeliveryEvent(StrictModel):
    event_id: UUID
    event_type: Literal["notification.delivery.received"]
    correlation_id: str = Field(min_length=1, max_length=120)
    payload: NotificationDeliveryCallbackRequest


class AlertWorkflowStep(str, Enum):
    PROJECT = "project"
    THRESHOLD = "threshold"
    SCHEDULE = "schedule"
    RESEND = "resend"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"


class AlertWorkflowStatus(str, Enum):
    ACTIVE = "active"
    READY_FOR_CONFIRMATION = "ready_for_confirmation"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AlertWorkflowOption(StrictModel):
    value: str
    label: str
    description: str | None = None


class AlertWorkflowQuestion(StrictModel):
    step: AlertWorkflowStep
    prompt: str
    input_type: Literal["single_select", "number"]
    options: list[AlertWorkflowOption] = Field(default_factory=list)


class StartAlertWorkflowRequest(StrictModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    conversation_id: str = Field(min_length=1, max_length=160)
    interaction_id: str | None = Field(default=None, max_length=160)
    parameters: dict[str, Any] = Field(default_factory=dict)


class AnswerAlertWorkflowRequest(StrictModel):
    step: AlertWorkflowStep
    value: Any
    revision: int = Field(ge=0)
    client_action_id: str = Field(min_length=8, max_length=160)


class ConfirmAlertWorkflowRequest(StrictModel):
    revision: int = Field(ge=0)
    client_action_id: str = Field(min_length=8, max_length=160)


class AlertWorkflowSession(StrictModel):
    session_id: str
    requested_by: str
    conversation_id: str
    interaction_id: str | None
    correlation_id: str
    status: AlertWorkflowStatus
    current_step: AlertWorkflowStep
    revision: int
    answers: dict[str, Any]
    action_ids: list[str]
    prepared: PrepareAlertResponse | None = None
    subscription_id: str | None = None
    created_at: datetime
    updated_at: datetime


class AlertWorkflowResponse(StrictModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    session_id: str
    workflow: Literal["alerta_prazo_atraso"] = "alerta_prazo_atraso"
    status: AlertWorkflowStatus
    current_step: AlertWorkflowStep
    revision: int
    question: AlertWorkflowQuestion | None = None
    answers: dict[str, Any]
    confirmation_summary: str | None = None
    warnings: list[str] = Field(default_factory=list)
    subscription: AlertSubscription | None = None

    @field_validator("warnings")
    @classmethod
    def unique_warnings(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))
