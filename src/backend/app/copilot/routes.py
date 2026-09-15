"""Rotas HTTP da integracao segura com Copilot Studio e Direct Line."""

from __future__ import annotations

import logging
import os
import re
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, Response

from app.copilot.direct_line import issue_direct_line_token
from app.copilot.errors import CopilotConfigurationError
from app.copilot.guard import ensure_safe_dispatch_input
from app.copilot.model_routing import resolve_model_route
from app.copilot.schemas import (
    CopilotDispatchRequest,
    CopilotDispatchResponse,
    DirectLineTokenResponse,
)
from app.copilot.security import (
    CopilotIdentity,
    require_copilot_channel,
    require_copilot_invoke,
)
from app.database.tracing import (
    TraceabilityError,
    is_tracing_configured,
    trace_audit_event,
    trace_interaction,
)
from app.gemini.client import GeminiConfigurationError
from app.gemini.schemas import GeminiChatRequest
from app.pipeline import ClassificationOutcome, classify_message

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Copilot Studio"])

_CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")


@router.post(
    "/api/integrations/copilot/dispatch",
    response_model=CopilotDispatchResponse,
    summary="Classificar e autorizar despacho solicitado pelo Copilot Studio",
)
def dispatch_from_copilot(
    payload: CopilotDispatchRequest,
    request: Request,
    _identity: Annotated[CopilotIdentity, Depends(require_copilot_invoke)],
) -> CopilotDispatchResponse:
    correlation_id = request.state.correlation_id
    execution_id = uuid4()
    model_route = resolve_model_route(payload.model_route)
    ensure_safe_dispatch_input(payload.message)
    started_at = perf_counter()

    try:
        classification = classify_message(payload.message)
    except GeminiConfigurationError as error:
        raise CopilotConfigurationError() from error

    route_taken = _route_taken(classification)
    status = (
        "accepted"
        if classification.routed and route_taken != "fora_escopo"
        else "blocked"
    )
    interaction_id = _trace_dispatch(
        payload=payload,
        classification=classification,
        correlation_id=correlation_id,
        execution_id=str(execution_id),
        model_route=model_route,
        route_taken=route_taken,
        processing_ms=round((perf_counter() - started_at) * 1000),
    )
    return CopilotDispatchResponse(
        correlation_id=correlation_id,
        request_id=payload.request_id,
        execution_id=execution_id,
        interaction_id=interaction_id,
        status=status,
        route_taken=route_taken,
        model_route=model_route,
        intent=classification.intent,
        entities=classification.entities,
    )


@router.post(
    "/api/copilot/token",
    response_model=DirectLineTokenResponse,
    summary="Emitir token temporario para uma conversa Direct Line",
)
async def create_copilot_channel_token(
    request: Request,
    http_response: Response,
    identity: Annotated[CopilotIdentity, Depends(require_copilot_channel)],
) -> DirectLineTokenResponse:
    response = await issue_direct_line_token(identity)
    _audit_safely(
        event_type="direct_line_token_issued",
        event_status="sucesso",
        correlation_id=request.state.correlation_id,
        payload={"conversation_id": response.conversation_id},
        required=_audit_required(),
    )
    http_response.headers["Cache-Control"] = "no-store"
    http_response.headers["Pragma"] = "no-cache"
    return response


def correlation_id_from_request(request: Request) -> str:
    supplied = request.headers.get("X-Correlation-ID", "").strip()
    if supplied and _CORRELATION_ID_PATTERN.fullmatch(supplied):
        return supplied
    return str(uuid4())


def audit_copilot_failure(request: Request, *, code: str, status_code: int) -> None:
    """Registra somente metadados seguros; credencial e payload nunca entram."""

    event_status = "bloqueado" if status_code in {400, 401, 403, 422} else "falha"
    _audit_safely(
        event_type="copilot_request_rejected",
        event_status=event_status,
        correlation_id=request.state.correlation_id,
        payload={"code": code, "http_status": status_code},
    )


def _route_taken(classification: ClassificationOutcome) -> str:
    if not classification.routed or classification.intent.macro in {
        "FORA_DE_ESCOPO",
        "INDEFINIDA",
    }:
        return "fora_escopo"
    if classification.intent.macro == "CONSULTA":
        return "sharepoint_query"
    return "copilot_topic"


def _trace_dispatch(
    *,
    payload: CopilotDispatchRequest,
    classification: ClassificationOutcome,
    correlation_id: str,
    execution_id: str,
    model_route: str,
    route_taken: str,
    processing_ms: int,
) -> str | None:
    try:
        interaction_id = trace_interaction(
            request=GeminiChatRequest(message=payload.message),
            response=None,
            intent=classification.intent,
            entities=classification.entities,
            processing_ms=processing_ms,
            channel="copilot_studio",
            external_conversation_id=payload.conversation_id,
            correlation_id=correlation_id,
            route_taken=route_taken,
            audit_context={
                "request_id": str(payload.request_id),
                "execution_id": execution_id,
                "model_route": model_route,
                "route_taken": route_taken,
            },
        )
    except TraceabilityError as error:
        logger.warning("Falha controlada ao registrar despacho do Copilot Studio.")
        if _audit_required():
            raise CopilotConfigurationError() from error
        return None

    if interaction_id is None and _audit_required():
        raise CopilotConfigurationError()
    return interaction_id


def _audit_required() -> bool:
    raw = os.getenv("COPILOT_AUDIT_REQUIRED", "0").strip()
    if raw not in {"0", "1"}:
        raise CopilotConfigurationError()
    return raw == "1"


def _audit_safely(
    *,
    event_type: str,
    event_status: str,
    correlation_id: str,
    payload: dict[str, object],
    required: bool = False,
) -> None:
    if required and not is_tracing_configured():
        raise CopilotConfigurationError()
    try:
        trace_audit_event(
            event_type=event_type,
            component="copilot_studio",
            event_status=event_status,
            correlation_id=correlation_id,
            payload=payload,
        )
    except TraceabilityError as error:
        logger.warning("Falha controlada ao registrar evento do Copilot Studio.")
        if required:
            raise CopilotConfigurationError() from error
