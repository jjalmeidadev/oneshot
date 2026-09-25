"""Entrada comum de texto e transcricao para classificacao, resposta e tracing."""

import logging
from threading import Lock
from time import perf_counter

from app.database.tracing import TraceabilityError, trace_interaction
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    execute_proactive_confirmation,
    generate_chat_response,
)
from app.gemini.schemas import (
    GeminiChatRequest,
    GeminiChatResponse,
    GeminiUsage,
    ProactiveConfirmationRequest,
    ProactiveConfirmationResponse,
)
from app.nlp.entities import Entidade, extract_entities
from app.nlp.schemas import (
    AudioIntent,
    ChatPipelineMetrics,
    IntentAlternative,
    PublicEntity,
)

_classifier_lock = Lock()
logger = logging.getLogger(__name__)


def warmup_classifier() -> None:
    """Prepara o modelo uma vez antes de atender usuarios quando habilitado."""
    from app.nlp.inference import get_classifier

    with _classifier_lock:
        get_classifier().warmup()


def process_message(
    request: GeminiChatRequest,
    *,
    channel: str = "api",
    external_conversation_id: str | None = None,
    requester_id: str | None = None,
) -> GeminiChatResponse:
    route_started_at = perf_counter()
    intent = None
    fallback_to_rag = False
    nlp_ms = 0
    entities: list[PublicEntity] = []

    if request.use_intent_classifier:
        nlp_started_at = perf_counter()
        try:
            from app.nlp.inference import classify

            with _classifier_lock:
                result = classify(request.message)
            entities = [
                _public_entity(entity)
                for entity in extract_entities(request.message)
            ]
            nlp_ms = _elapsed_ms(nlp_started_at)
        except Exception as error:
            _trace_safely(
                request=request,
                response=None,
                intent=None,
                entities=[],
                processing_ms=_elapsed_ms(route_started_at),
                channel=channel,
                external_conversation_id=external_conversation_id,
                error_message=str(error),
                requester_id=requester_id,
            )
            raise GeminiConfigurationError("Classificador indisponivel.") from error

        intent = _public_intent(result)
        fallback_to_rag = (
            not result.roteada
            or result.macrointencao == "FORA_DE_ESCOPO"
            or result.intencao is None
        )

        if (
            not fallback_to_rag
            and result.handler == "handler:transacao_gerar_relatorio"
        ):
            response = _report_workflow_response(
                intent=intent,
                entities=entities,
                nlp_ms=nlp_ms,
                route_started_at=route_started_at,
            )
            _trace_safely(
                request=request,
                response=response,
                intent=intent,
                entities=entities,
                processing_ms=response.pipeline_metrics.route_ms,
                channel=channel,
                external_conversation_id=external_conversation_id,
                requester_id=requester_id,
            )
            return response

    try:
        provider_kwargs = {
            "intent": None if fallback_to_rag else intent,
            "entities": entities,
        }
        if fallback_to_rag:
            provider_kwargs["require_rag_context"] = True
        if requester_id is not None and request.proactivity_enabled:
            provider_kwargs["requester_id"] = requester_id
        response = generate_chat_response(request, **provider_kwargs)
    except (GeminiConfigurationError, GeminiAPIError) as error:
        _trace_safely(
            request=request,
            response=None,
            intent=intent,
            entities=entities,
            processing_ms=_elapsed_ms(route_started_at),
            channel=channel,
            external_conversation_id=external_conversation_id,
            error_message=str(error),
            requester_id=requester_id,
        )
        raise

    response.intent = intent
    response.entities = entities
    response.pipeline_metrics = ChatPipelineMetrics(
        nlp_ms=nlp_ms,
        route_ms=_elapsed_ms(route_started_at),
    )
    _trace_safely(
        request=request,
        response=response,
        intent=intent,
        entities=entities,
        processing_ms=response.pipeline_metrics.route_ms,
        channel=channel,
        external_conversation_id=external_conversation_id,
        requester_id=requester_id,
    )
    return response


def process_proactive_confirmation(
    request: ProactiveConfirmationRequest,
    *,
    requester_id: str,
) -> ProactiveConfirmationResponse:
    """Confirma a sugestao e registra a resposta secundaria no RNF03."""

    started_at = perf_counter()
    execution = execute_proactive_confirmation(request, requester_id=requester_id)
    if execution.response.result is None:
        return execution.response

    pending = execution.pending
    intent = AudioIntent(
        macro="CONSULTA",
        specific=pending.secondary_intent.name,
        confidence_macro=1.0,
        confidence_specific=1.0,
        flow="Confirmacao proativa",
        handler="proactive_confirmation",
    )
    trace_request = GeminiChatRequest(
        message=f"Confirmar sugestao: {pending.secondary_intent.name}",
        conversation_id=pending.conversation_id,
        use_intent_classifier=False,
    )
    _trace_safely(
        request=trace_request,
        response=execution.response.result,
        intent=intent,
        entities=[],
        processing_ms=_elapsed_ms(started_at),
        requester_id=requester_id,
    )
    return execution.response


def _report_workflow_response(
    *,
    intent: AudioIntent,
    entities: list[PublicEntity],
    nlp_ms: int,
    route_started_at: float,
) -> GeminiChatResponse:
    """Despacha a transacao sem enviar o pedido ao provedor generativo."""

    from app.reports.schemas import WorkflowDirective

    scope_candidates = [
        {"type": entity.type, "value": entity.value}
        for entity in entities
        if entity.type in {"projeto", "subportfolio"}
    ]
    return GeminiChatResponse(
        text=(
            "Vou conduzir a geracao do relatorio. Antes de iniciar, preciso "
            "confirmar escopo, periodo, publico, finalidade e enfase."
        ),
        model="workflow-router",
        latency_ms=0,
        usage=GeminiUsage(),
        intent=intent,
        entities=entities,
        pipeline_metrics=ChatPipelineMetrics(
            nlp_ms=nlp_ms,
            route_ms=_elapsed_ms(route_started_at),
        ),
        workflow=WorkflowDirective(
            parameters={"scope_candidates": scope_candidates},
        ),
    )


def _public_entity(entity: Entidade) -> PublicEntity:
    return PublicEntity(
        type=entity.tipo,
        value=entity.valor,
        text=entity.texto,
        start=entity.inicio,
        end=entity.fim,
        types=list(entity.tipos),
        ambiguous=entity.ambigua,
    )


def _public_intent(result: object) -> AudioIntent:
    alternatives = getattr(result, "alternativas", [])
    return AudioIntent(
        macro=result.macrointencao,
        specific=result.intencao or "",
        confidence_macro=result.confianca_macro,
        confidence_specific=result.confianca_intencao,
        flow=getattr(result, "fluxo", ""),
        handler=getattr(result, "handler", ""),
        alternatives=[
            IntentAlternative(intent=alternative, confidence=confidence)
            for alternative, confidence in alternatives
        ],
    )


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)


def _trace_safely(
    *,
    request: GeminiChatRequest,
    response: GeminiChatResponse | None,
    intent: AudioIntent | None,
    entities: list[PublicEntity],
    processing_ms: int,
    channel: str = "api",
    external_conversation_id: str | None = None,
    error_message: str | None = None,
    requester_id: str | None = None,
) -> None:
    try:
        trace_interaction(
            request=request,
            response=response,
            intent=intent,
            entities=entities,
            processing_ms=processing_ms,
            channel=channel,
            external_conversation_id=external_conversation_id,
            error_message=error_message,
            requester_id=requester_id,
        )
    except TraceabilityError:
        logger.warning("Falha controlada ao registrar rastreabilidade RNF03.")
