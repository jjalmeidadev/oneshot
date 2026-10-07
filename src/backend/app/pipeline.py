"""Entrada comum de texto e transcricao para classificacao, resposta e tracing."""

import logging
from threading import Lock
from time import perf_counter

from app.database.tracing import TraceabilityError, trace_interaction
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    SensitiveDataBlockedError,
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
from app.security.sensitive_data import SensitiveDataReport, describe_categories, scan
from app.nlp.schemas import (
    AudioIntent,
    ChatPipelineMetrics,
    IntentAlternative,
    PublicEntity,
)
from app.security.access import AccessContext

_classifier_lock = Lock()
logger = logging.getLogger(__name__)

#: Modelo informado na resposta quando a pergunta e barrada pelo RNF01.
SENSITIVE_BLOCK_MODEL = "bloqueio-dado-sensivel"
#: Registrado como falha controlada: `processing_status` nao tem `bloqueado`,
#: e o evento `sensitive_content_blocked` traz o detalhe (decisao da S5-27).
SENSITIVE_BLOCK_ERROR = "Dado sensivel bloqueado antes do provedor."


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
    user_id: str | None = None,
    access_context: AccessContext | None = None,
) -> GeminiChatResponse:
    route_started_at = perf_counter()

    # RNF01, primeira barreira: pergunta com dado sensivel nao segue para
    # classificacao nem para o provedor, e a auditoria so recebe a versao
    # mascarada.
    blocked = _block_sensitive_message(
        request,
        route_started_at=route_started_at,
        channel=channel,
        external_conversation_id=external_conversation_id,
        requester_id=requester_id,
        user_id=user_id,
    )
    if blocked is not None:
        return blocked

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
                user_id=user_id,
            )
            raise GeminiConfigurationError("Classificador indisponivel.") from error

        intent = _public_intent(result)
        from app.nlp.routing import SCHEDULING_LIMITATION_HANDLER

        if result.handler == SCHEDULING_LIMITATION_HANDLER:
            response = GeminiChatResponse(
                text=result.resposta_sugerida,
                model="domain-router",
                latency_ms=0,
                usage=GeminiUsage(input_tokens=0, output_tokens=0, total_tokens=0),
                intent=intent,
                entities=entities,
                pipeline_metrics=ChatPipelineMetrics(
                    nlp_ms=nlp_ms, route_ms=_elapsed_ms(route_started_at),
                ),
            )
            _trace_safely(
                request=request, response=response, intent=intent, entities=entities,
                processing_ms=response.pipeline_metrics.route_ms, channel=channel,
                external_conversation_id=external_conversation_id,
                requester_id=requester_id, user_id=user_id,
            )
            return response

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
                user_id=user_id,
            )
            return response

        if result.handler == "handler:alerta_prazo_atraso":
            response = _alert_workflow_response(
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
                requester_id=requester_id,
                user_id=user_id,
            )
            return response

    try:
        provider_kwargs = {
            "intent": None if fallback_to_rag else intent,
            "entities": entities,
            "access_context": access_context,
        }
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
            security_report=(
                error.report.audit_payload()
                if isinstance(error, SensitiveDataBlockedError)
                else None
            ),
            user_id=user_id,
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
        user_id=user_id,
    )
    return response


def process_proactive_confirmation(
    request: ProactiveConfirmationRequest,
    *,
    requester_id: str,
    user_id: str | None = None,
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
        user_id=user_id,
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


def _alert_workflow_response(
    *,
    intent: AudioIntent,
    entities: list[PublicEntity],
    nlp_ms: int,
    route_started_at: float,
) -> GeminiChatResponse:
    """Inicia a configuracao interna sem chamar um provedor generativo."""

    from app.alerts.schemas import AlertDirective

    parameters: dict[str, object] = {
        "scope_candidates": [
            {"type": entity.type, "value": entity.value}
            for entity in entities
            if entity.type == "projeto"
        ]
    }
    deadline = next((entity.value for entity in entities if entity.type == "prazo_dias"), None)
    if deadline:
        digits = "".join(character for character in deadline if character.isdigit())
        if digits:
            parameters["threshold_days"] = int(digits)
    return GeminiChatResponse(
        text=(
            "Vou configurar um alerta autonomo de prazo. Antes de ativar, "
            "preciso confirmar o projeto, o limiar e a recorrencia."
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
        workflow=AlertDirective(parameters=parameters),
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
        routing_rule=getattr(result, "regra_roteamento", None),
        alternatives=[
            IntentAlternative(intent=alternative, confidence=confidence)
            for alternative, confidence in alternatives
        ],
    )


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)


def _block_sensitive_message(
    request: GeminiChatRequest,
    *,
    route_started_at: float,
    channel: str,
    external_conversation_id: str | None,
    requester_id: str | None,
    user_id: str | None = None,
) -> GeminiChatResponse | None:
    """Barra a pergunta com dado sensivel antes de qualquer servico externo."""

    found = scan(request.message)
    if not found.found:
        return None

    report = SensitiveDataReport(stage="mensagem", action="bloqueado", counts=found.counts)
    response = GeminiChatResponse(
        text=(
            f"Sua mensagem contém {describe_categories(found.categories)}. "
            "Por segurança, ela não foi enviada ao modelo de linguagem. "
            "Remova o dado e envie a pergunta novamente."
        ),
        model=SENSITIVE_BLOCK_MODEL,
        latency_ms=0,
        usage=GeminiUsage(),
        evidence_status="not_applicable",
        security_report=report.audit_payload(),
        pipeline_metrics=ChatPipelineMetrics(
            nlp_ms=0,
            route_ms=_elapsed_ms(route_started_at),
        ),
    )
    _trace_safely(
        request=request.model_copy(update={"message": found.masked}),
        response=response,
        intent=None,
        entities=[],
        processing_ms=response.pipeline_metrics.route_ms,
        channel=channel,
        external_conversation_id=external_conversation_id,
        error_message=SENSITIVE_BLOCK_ERROR,
        requester_id=requester_id,
        user_id=user_id,
    )
    return response


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
    security_report: dict | None = None,
    user_id: str | None = None,
) -> None:
    try:
        trace_id = trace_interaction(
            request=request,
            response=response,
            intent=intent,
            entities=entities,
            processing_ms=processing_ms,
            channel=channel,
            external_conversation_id=external_conversation_id,
            error_message=error_message,
            requester_id=requester_id,
            security_report=security_report,
            user_id=user_id,
        )
        if response is not None:
            response.trace_id = trace_id
    except TraceabilityError:
        logger.warning("Falha controlada ao registrar rastreabilidade RNF03.")
