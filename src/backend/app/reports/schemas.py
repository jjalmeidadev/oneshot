"""Contratos versionados do fluxo transacao_gerar_relatorio."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CONTRACT_VERSION = "1.0"


class StrictContractModel(BaseModel):
    """Base comum dos contratos: campos desconhecidos nunca sao ignorados."""

    model_config = ConfigDict(extra="forbid")


class ScopeType(str, Enum):
    PROJECT = "project"
    SUBPORTFOLIO = "subportfolio"


class ReportType(str, Enum):
    EXECUTIVE_STATUS = "executive_status"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    CLARIFYING = "clarifying"
    READY_FOR_CONFIRMATION = "ready_for_confirmation"
    CONFIRMED = "confirmed"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Audience(str, Enum):
    EXECUTIVE_BOARD = "executive_board"
    PMO = "pmo"
    PROJECT_TEAM = "project_team"


class Purpose(str, Enum):
    MONTHLY_GOVERNANCE = "monthly_governance"
    DECISION_SUPPORT = "decision_support"
    STATUS_COMMUNICATION = "status_communication"


class Emphasis(str, Enum):
    SCHEDULE = "schedule"
    RISKS = "risks"
    BENEFITS = "benefits"
    CHANGES = "changes"
    MILESTONES = "milestones"


# Mapa deterministico de texto livre (pt-BR) para o enum Emphasis.
# Usado para normalizar a entrada do topico (Topic.EmphasisText) sem LLM.
_EMPHASIS_KEYWORDS: dict[str, Emphasis] = {
    "cronograma": Emphasis.SCHEDULE,
    "prazo": Emphasis.SCHEDULE,
    "prazos": Emphasis.SCHEDULE,
    "atraso": Emphasis.SCHEDULE,
    "atrasos": Emphasis.SCHEDULE,
    "schedule": Emphasis.SCHEDULE,
    "risco": Emphasis.RISKS,
    "riscos": Emphasis.RISKS,
    "risks": Emphasis.RISKS,
    "beneficio": Emphasis.BENEFITS,
    "beneficios": Emphasis.BENEFITS,
    "benefits": Emphasis.BENEFITS,
    "mudanca": Emphasis.CHANGES,
    "mudancas": Emphasis.CHANGES,
    "changes": Emphasis.CHANGES,
    "marco": Emphasis.MILESTONES,
    "marcos": Emphasis.MILESTONES,
    "entrega": Emphasis.MILESTONES,
    "entregas": Emphasis.MILESTONES,
    "milestones": Emphasis.MILESTONES,
}


def normalize_emphasis(raw: str | None) -> list[Emphasis]:
    """Converte texto livre em uma lista deterministica de Emphasis.

    Normalizacao puramente lexical (sem LLM): remove acentos, quebra por
    separadores comuns e mapeia por palavra-chave. Termos desconhecidos sao
    ignorados; entrada vazia retorna lista vazia (visao geral). Preserva a
    ordem de aparicao e nao duplica valores.
    """
    if not raw:
        return []
    lowered = raw.casefold()
    stripped = (
        lowered.replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    for separator in (",", ";", "/", " e ", " and "):
        stripped = stripped.replace(separator, " ")
    result: list[Emphasis] = []
    for token in stripped.split():
        mapped = _EMPHASIS_KEYWORDS.get(token)
        if mapped is not None and mapped not in result:
            result.append(mapped)
    return result[:5]


class OutputFormat(str, Enum):
    DOCX = "docx"


class ReportScope(StrictContractModel):
    type: ScopeType
    id: str = Field(min_length=1, max_length=120)

    @field_validator("id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Escopo vazio")
        return value


class ReportPeriod(StrictContractModel):
    start_date: date
    end_date: date
    label: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def validate_period(self) -> ReportPeriod:
        if self.end_date < self.start_date:
            raise ValueError("A data final deve ser igual ou posterior a data inicial")
        if (self.end_date - self.start_date).days > 366:
            raise ValueError("O periodo de referencia nao pode exceder 366 dias")
        return self


class ReportOptions(StrictContractModel):
    audience: Audience
    purpose: Purpose
    emphasis: list[Emphasis] = Field(default_factory=list, max_length=5)
    emphasis_text: str | None = Field(default=None, max_length=200, exclude=True)
    additional_context: str | None = Field(default=None, max_length=4000)
    output_format: OutputFormat = OutputFormat.DOCX

    @field_validator("additional_context")
    @classmethod
    def normalize_context(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @model_validator(mode="after")
    def resolve_emphasis(self) -> ReportOptions:
        # Se a enfase estruturada nao veio, deriva deterministicamente do texto
        # livre coletado pelo topico (Topic.EmphasisText). Sem LLM.
        if not self.emphasis and self.emphasis_text:
            self.emphasis = normalize_emphasis(self.emphasis_text)
        return self


class PrepareReportRequest(StrictContractModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    conversation_id: str = Field(min_length=1, max_length=160)
    interaction_id: str | None = Field(default=None, max_length=160)
    correlation_id: str | None = Field(default=None, max_length=120)
    report_type: ReportType = ReportType.EXECUTIVE_STATUS
    scope: ReportScope
    period: ReportPeriod
    options: ReportOptions

class PreparedReport(StrictContractModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    requested_by: str
    conversation_id: str
    interaction_id: str | None = None
    correlation_id: str
    report_type: ReportType
    scope: ReportScope
    period: ReportPeriod
    options: ReportOptions
    scope_title: str
    data_reference_at: datetime
    confirmation_expires_at: datetime


class PrepareReportResponse(StrictContractModel):
    status: ReportStatus = ReportStatus.READY_FOR_CONFIRMATION
    prepared_request: PreparedReport
    confirmation_summary: str
    confirmation_hash: str
    expires_at: datetime
    warnings: list[str] = Field(default_factory=list)


class CreateReportRequest(StrictContractModel):
    prepared_request: PreparedReport
    confirmation_hash: str = Field(min_length=64, max_length=64)
    idempotency_key: str = Field(min_length=8, max_length=160)

    @field_validator("idempotency_key")
    @classmethod
    def normalize_idempotency_key(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Chave de idempotencia vazia")
        return value


class ReportSource(StrictContractModel):
    source_id: str
    title: str
    source_type: str
    locator: str
    last_updated: datetime


class ReportArtifact(StrictContractModel):
    artifact_id: str
    file_name: str
    content_type: str
    size_bytes: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)
    download_url: str
    storage_provider: str
    storage_reference: str | None = Field(default=None, exclude=True)
    created_at: datetime


class ExecutiveSummaryResult(StrictContractModel):
    schema_version: Literal["1.0"] = "1.0"
    summary: str = Field(min_length=1, max_length=3000)
    citation_source_ids: list[str] = Field(default_factory=list, max_length=30)
    limitations: list[str] = Field(default_factory=list, max_length=30)


class NormalizedContextResult(StrictContractModel):
    schema_version: Literal["1.0"] = "1.0"
    normalized_text: str | None = Field(default=None, max_length=4000)
    removed_unsafe_content: bool = False
    warnings: list[str] = Field(default_factory=list, max_length=30)


class FoundationReviewResult(StrictContractModel):
    schema_version: Literal["1.0"] = "1.0"
    approved: bool
    unsupported_claims: list[str] = Field(default_factory=list, max_length=30)
    numeric_mismatches: list[str] = Field(default_factory=list, max_length=30)
    missing_source_ids: list[str] = Field(default_factory=list, max_length=30)
    warnings: list[str] = Field(default_factory=list, max_length=30)


class ReportAutomationResult(StrictContractModel):
    """Saida estruturada do Power Automate/AI Builder, nunca um arquivo externo."""

    schema_version: Literal["1.0"] = "1.0"
    executive_summary: ExecutiveSummaryResult | None = None
    normalized_context: NormalizedContextResult | None = None
    foundation_review: FoundationReviewResult | None = None
    prompt_versions: dict[str, str] = Field(default_factory=dict)


class ExecutionEvent(StrictContractModel):
    event_type: str
    status: str
    component: str
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class ReportExecution(StrictContractModel):
    execution_id: str
    correlation_id: str
    idempotency_key: str
    requested_by: str
    status: ReportStatus
    confirmation_hash: str = Field(min_length=64, max_length=64)
    prepared_request: PreparedReport
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    flow_run_id: str | None = None
    callback_id: str | None = None
    snapshot_hash: str | None = None
    snapshot_payload: dict[str, Any] | None = Field(default=None, exclude=True)
    sources: list[ReportSource] = Field(default_factory=list)
    artifact: ReportArtifact | None = None
    warnings: list[str] = Field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None
    events: list[ExecutionEvent] = Field(default_factory=list)


class ReportExecutionResponse(StrictContractModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    execution_id: str
    correlation_id: str
    status: ReportStatus
    status_url: str
    artifact: ReportArtifact | None = None
    warnings: list[str] = Field(default_factory=list)
    error: dict[str, str] | None = None
    created_at: datetime
    updated_at: datetime


class ReportCallbackRequest(StrictContractModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    callback_id: str = Field(min_length=8, max_length=160)
    execution_id: str = Field(min_length=1, max_length=160)
    correlation_id: str = Field(min_length=1, max_length=120)
    flow_run_id: str = Field(min_length=1, max_length=160)
    status: ReportStatus
    result: ReportAutomationResult | None = None
    warnings: list[str] = Field(default_factory=list, max_length=50)
    error_code: str | None = Field(default=None, max_length=80)
    error_message: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_terminal_callback(self) -> ReportCallbackRequest:
        terminal = {
            ReportStatus.COMPLETED,
            ReportStatus.COMPLETED_WITH_WARNINGS,
            ReportStatus.FAILED,
            ReportStatus.BLOCKED,
            ReportStatus.CANCELLED,
        }
        if self.status not in terminal:
            raise ValueError("Callback deve informar um estado terminal")
        if (
            self.status
            in {
                ReportStatus.COMPLETED,
                ReportStatus.COMPLETED_WITH_WARNINGS,
            }
            and self.result is None
        ):
            raise ValueError("Callback concluido deve informar o JSON estruturado")
        if (
            self.status in {ReportStatus.FAILED, ReportStatus.BLOCKED}
            and not self.error_code
        ):
            raise ValueError("Callback de falha ou bloqueio deve informar error_code")
        return self


class WorkflowDirective(StrictContractModel):
    kind: Literal["guided_workflow"] = "guided_workflow"
    action: Literal["start"] = "start"
    workflow: Literal["transacao_gerar_relatorio"] = "transacao_gerar_relatorio"
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    parameters: dict[str, Any] = Field(default_factory=dict)


class WorkflowStatus(str, Enum):
    ACTIVE = "active"
    READY_FOR_CONFIRMATION = "ready_for_confirmation"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowStep(str, Enum):
    SCOPE_TYPE = "scope_type"
    SCOPE = "scope"
    PERIOD = "period"
    AUDIENCE = "audience"
    PURPOSE = "purpose"
    EMPHASIS = "emphasis"
    ADDITIONAL_CONTEXT = "additional_context"
    CONFIRMATION = "confirmation"
    EXECUTION = "execution"


class WorkflowOption(StrictContractModel):
    value: str
    label: str
    description: str | None = None


class WorkflowQuestion(StrictContractModel):
    step: WorkflowStep
    prompt: str
    input_type: Literal["single_select", "multi_select", "date_range", "text"]
    required: bool = True
    options: list[WorkflowOption] = Field(default_factory=list)


class StartWorkflowRequest(StrictContractModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    conversation_id: str = Field(min_length=1, max_length=160)
    interaction_id: str | None = Field(default=None, max_length=160)
    parameters: dict[str, Any] = Field(default_factory=dict)


class AnswerWorkflowRequest(StrictContractModel):
    step: WorkflowStep
    value: Any = None
    revision: int = Field(ge=0)
    client_action_id: str = Field(min_length=8, max_length=160)


class ConfirmWorkflowRequest(StrictContractModel):
    revision: int = Field(ge=0)
    client_action_id: str = Field(min_length=8, max_length=160)


class WorkflowAnswer(StrictContractModel):
    step: WorkflowStep
    value: Any
    client_action_id: str
    answered_at: datetime


class WorkflowSession(StrictContractModel):
    session_id: str
    workflow: Literal["transacao_gerar_relatorio"] = "transacao_gerar_relatorio"
    requested_by: str
    conversation_id: str
    interaction_id: str | None = None
    correlation_id: str
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    current_step: WorkflowStep = WorkflowStep.SCOPE_TYPE
    revision: int = 0
    answers: dict[str, Any] = Field(default_factory=dict)
    answer_history: list[WorkflowAnswer] = Field(default_factory=list)
    prepared: PrepareReportResponse | None = None
    execution_id: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkflowSessionResponse(StrictContractModel):
    contract_version: Literal["1.0"] = CONTRACT_VERSION
    session_id: str
    workflow: str
    status: WorkflowStatus
    current_step: WorkflowStep
    revision: int
    question: WorkflowQuestion | None = None
    answers: dict[str, Any] = Field(default_factory=dict)
    confirmation_summary: str | None = None
    warnings: list[str] = Field(default_factory=list)
    execution: ReportExecutionResponse | None = None
