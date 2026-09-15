"""Entrada comum de texto e transcricao para classificacao, resposta e tracing."""

import logging
from dataclasses import dataclass
from threading import Lock
from time import perf_counter

from app.database.tracing import TraceabilityError, trace_interaction
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    generate_chat_response,
)
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse, GeminiUsage
from app.nlp.entities import Entidade, extract_entities
from app.nlp.schemas import (
    AudioIntent,
    ChatPipelineMetrics,
    IntentAlternative,
    PublicEntity,
)

_classifier_lock = Lock()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClassificationOutcome:
    """Resultado interno compartilhado pelas rotas de chat e Copilot."""

    intent: AudioIntent
    entities: list[PublicEntity]
    routed: bool
    suggested_response: str | None
    nlp_ms: int


def warmup_classifier() -> None:
    """Prepara o modelo uma vez antes de atender usuarios quando habilitado."""
    from app.nlp.inference import get_classifier

    with _classifier_lock:
        get_classifier().warmup()


def process_message(request: GeminiChatRequest) -> GeminiChatResponse:
    route_started_at = perf_counter()
    intent = None
    nlp_ms = 0
    entities: list[PublicEntity] = []

    if request.use_intent_classifier:
        classification = classify_message(request.message)
        intent = classification.intent
        entities = classification.entities
        nlp_ms = classification.nlp_ms
        if not classification.routed or intent.macro == "FORA_DE_ESCOPO":
            response = GeminiChatResponse(
                text=classification.suggested_response
                or "Posso ajudar com informações do portfólio. Reformule sua pergunta indicando um projeto ou documento.",
                model="classificador-local",
                latency_ms=0,
                usage=GeminiUsage(),
                intent=intent,
                entities=entities,
                pipeline_metrics=ChatPipelineMetrics(
                    nlp_ms=nlp_ms,
                    route_ms=_elapsed_ms(route_started_at),
                ),
            )
            _trace_safely(
                request=request,
                response=response,
                intent=intent,
                entities=entities,
                processing_ms=_elapsed_ms(route_started_at),
            )
            return response

    try:
        response = generate_chat_response(request, intent=intent, entities=entities)
    except (GeminiConfigurationError, GeminiAPIError) as error:
        _trace_safely(
            request=request,
            response=None,
            intent=intent,
            entities=entities,
            processing_ms=_elapsed_ms(route_started_at),
            error_message=str(error),
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
    )
    return response


def classify_message(message: str) -> ClassificationOutcome:
    """Executa o nucleo autoral de PLN sem acionar um provedor generativo."""

    nlp_started_at = perf_counter()
    try:
        from app.nlp.inference import classify

        with _classifier_lock:
            result = classify(message)
        entities = [_public_entity(entity) for entity in extract_entities(message)]
    except Exception as error:
        raise GeminiConfigurationError("Classificador indisponivel.") from error

    return ClassificationOutcome(
        intent=_public_intent(result),
        entities=entities,
        routed=bool(result.roteada),
        suggested_response=getattr(result, "resposta_sugerida", None),
        nlp_ms=_elapsed_ms(nlp_started_at),
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
    error_message: str | None = None,
) -> None:
    try:
        trace_interaction(
            request=request,
            response=response,
            intent=intent,
            entities=entities,
            processing_ms=processing_ms,
            error_message=error_message,
        )
    except TraceabilityError:
        logger.warning("Falha controlada ao registrar rastreabilidade RNF03.")
