"""Rotas do cartao de alteracao (S5-05, Secao 8.5.13).

Todas exigem leitura autenticada para entrar; a escrita e verificada pelo
servico na regra que cobre o projeto, na previa, na confirmacao e no desfazer.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from starlette.concurrency import run_in_threadpool

from app.data_changes import errors
from app.data_changes.schemas import (
    CancelResponse,
    ConfirmRequest,
    ConfirmResponse,
    DataChangeOutcome,
    HistoryResponse,
    PreviewRequest,
    UndoResponse,
)
from app.data_changes.service import DataChangeService, get_data_change_service
from app.security.access import AccessContext
from app.security.http import require_read_access

router = APIRouter(tags=["alteracao-dados"])
ReadAccess = Annotated[AccessContext, Depends(require_read_access)]


def require_service() -> DataChangeService:
    service = get_data_change_service()
    if service is None:
        raise errors.unavailable()
    return service


Service = Annotated[DataChangeService, Depends(require_service)]


@router.post("/api/data-change-previews", response_model=DataChangeOutcome)
async def create_data_change_preview(
    request: PreviewRequest,
    access: ReadAccess,
    service: Service,
) -> DataChangeOutcome:
    return await run_in_threadpool(service.create_preview, request, access)


@router.post("/api/data-change-previews/{pending_change_id}/confirm", response_model=ConfirmResponse)
async def confirm_data_change(
    pending_change_id: str,
    access: ReadAccess,
    service: Service,
    request: ConfirmRequest | None = None,
) -> ConfirmResponse:
    reason = request.reason if request else None
    return await run_in_threadpool(service.confirm, _uuid(pending_change_id, "PREVIEW_NOT_FOUND"), access, reason)


@router.post("/api/data-change-previews/{pending_change_id}/cancel", response_model=CancelResponse)
async def cancel_data_change(
    pending_change_id: str,
    access: ReadAccess,
    service: Service,
) -> CancelResponse:
    return await run_in_threadpool(service.cancel, _uuid(pending_change_id, "PREVIEW_NOT_FOUND"), access)


@router.post("/api/data-changes/{change_id}/undo", response_model=UndoResponse)
async def undo_data_change(
    change_id: str,
    access: ReadAccess,
    service: Service,
) -> UndoResponse:
    return await run_in_threadpool(service.undo, _uuid(change_id, "CHANGE_NOT_FOUND"), access)


@router.get("/api/data-changes", response_model=HistoryResponse)
async def list_data_changes(
    access: ReadAccess,
    service: Service,
    project_code: Annotated[str, Query(min_length=3, max_length=40)],
    field: Annotated[str, Query(min_length=3, max_length=60)],
    target_id: Annotated[str | None, Query(max_length=36)] = None,
) -> HistoryResponse:
    return await run_in_threadpool(service.history, project_code, field, target_id, access)


def _uuid(value: str, not_found_code: str) -> str:
    """Um identificador malformado e tratado como inexistente, sem ir ao banco."""

    from uuid import UUID

    try:
        return str(UUID(value))
    except ValueError as error:
        spec = errors.PREVIEW_NOT_FOUND if not_found_code == "PREVIEW_NOT_FOUND" else errors.CHANGE_NOT_FOUND
        raise errors.error(spec) from error
