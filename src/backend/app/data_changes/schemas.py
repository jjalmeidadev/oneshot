"""Contratos HTTP da alteracao de dados pelo chat (S5-05, Secao 8.5.13)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DATA_CHANGE_CONTRACT = "s5-05/v1"
DATA_CHANGE_MODEL = "alteracao-dados-chat"


class FieldRef(BaseModel):
    key: str
    label: str


class ValueView(BaseModel):
    """Valor canonico (para comparar) e exibido (para a pessoa)."""

    value: str | None
    display: str


class ProjectRef(BaseModel):
    code: str
    title: str


class TargetView(BaseModel):
    entity: Literal["projeto", "cronograma", "marco", "risco"]
    id: str
    label: str


class DataChangePreview(BaseModel):
    pending_change_id: str
    project: ProjectRef
    target: TargetView
    field: FieldRef
    before: ValueView
    after: ValueView
    warnings: list[str] = Field(default_factory=list)
    expires_at: datetime
    undo_window_minutes: int


class Candidate(BaseModel):
    id: str
    label: str


class DataChangeDraft(BaseModel):
    """O que ja foi entendido do pedido, para a interface completar."""

    project_code: str | None = None
    entity: Literal["projeto", "cronograma", "marco", "risco"] | None = None
    field: str | None = None
    target_id: str | None = None
    item_reference: str | None = None
    raw_value: str | None = None


class DataChangeOutcome(BaseModel):
    """Campo `data_change` da resposta do chat."""

    status: Literal["preview", "needs_input", "rejected"]
    preview: DataChangePreview | None = None
    missing: Literal["project", "target", "field", "value"] | None = None
    question: str | None = None
    candidates: list[Candidate] = Field(default_factory=list)
    draft: DataChangeDraft | None = None
    code: str | None = None
    message: str | None = None


class PreviewRequest(BaseModel):
    """Cria a previa a partir de uma proposta completa (escolha de candidato)."""

    model_config = ConfigDict(extra="forbid")

    project_code: str = Field(min_length=3, max_length=40)
    entity: Literal["projeto", "cronograma", "marco", "risco"] | None = None
    field: str = Field(min_length=3, max_length=60)
    target_id: str | None = Field(default=None, max_length=36)
    item_reference: str | None = Field(default=None, max_length=240)
    raw_value: str | None = Field(default=None, max_length=240)
    conversation_id: str | None = Field(default=None, max_length=160)


class ConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = Field(default=None, max_length=500)


class ConfirmResponse(BaseModel):
    change_id: str
    status: Literal["aplicada"]
    field: FieldRef
    target: TargetView
    before: ValueView
    after: ValueView
    applied_at: datetime
    undo_available_until: datetime
    correlation_id: str


class CancelResponse(BaseModel):
    status: Literal["cancelada"]


class UndoResponse(BaseModel):
    change_id: str
    status: Literal["desfeita"]
    restored: ValueView
    undone_at: datetime


class HistoryItem(BaseModel):
    change_id: str
    field: FieldRef
    target: TargetView
    before: ValueView
    after: ValueView
    requested_by: str
    applied_at: datetime
    status: Literal["aplicada", "desfeita"]
    undone_at: datetime | None = None
    can_undo: bool = False
    undo_available_until: datetime | None = None


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
