import json
import logging
import os
from dataclasses import dataclass
from time import perf_counter, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.database.connection import DatabaseConfigurationError, DatabaseConnectionError
from app.gemini.schemas import (
    GeminiChatRequest,
    GeminiChatResponse,
    GeminiSource,
    GeminiUsage,
    ProactiveConfirmationRequest,
    ProactiveConfirmationResponse,
    ProactiveSuggestion,
)
from app.nlp.schemas import AudioIntent, PublicEntity
from app.rag.database import retrieve_context
from app.rag.errors import RagSourceError
from app.rag.proactive_confirmation import (
    PendingProactiveSuggestion,
    claim_pending_suggestion,
    complete_pending_suggestion,
    decline_pending_suggestion,
    register_pending_suggestion,
)
from app.rag.proactivity import SecondaryIntent, resolve_secondary_intent
from app.rag.sharepoint import build_rag_input
from app.gemini.blocks import build_blocks
from app.security.sensitive_data import SensitiveDataReport, protect_documents, scan
from app.gemini.evidence import ValidatedAnswer, validate_evidence
from app.security.access import AccessContext

GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_MAX_OUTPUT_TOKENS = 1024
AVISO_RESPOSTA_INTERROMPIDA = (
    "*A resposta foi interrompida antes de terminar. "
    "Pergunte de novo, de forma mais específica.*"
)
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_DELAY_SECONDS = 2.0
RETRYABLE_HTTP_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
VALID_THINKING_LEVELS = frozenset({"minimal", "low", "medium", "high"})

#: Provedores de LLM aceitos em `LLM_PROVIDER`. O padrao continua sendo o Gemini
#: direto; o OpenRouter entra como alternativa selecionada por configuracao.
LLM_PROVIDER_GEMINI = "gemini"
LLM_PROVIDER_OPENROUTER = "openrouter"
VALID_LLM_PROVIDERS = frozenset({LLM_PROVIDER_GEMINI, LLM_PROVIDER_OPENROUTER})

OUT_OF_SCOPE_ANSWER = (
    "Essa solicitação não está no escopo da base de conhecimento disponível."
)

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "google/gemini-3.7-flash"
logger = logging.getLogger(__name__)


class GeminiConfigurationError(RuntimeError):
    pass


class GeminiAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class SensitiveDataBlockedError(GeminiAPIError):
    """A guarda final encontrou dado sensivel no prompt e recusou a chamada.

    So deve ocorrer se um caminho novo montar o prompt sem passar pelas
    barreiras da pergunta e dos documentos. ``report`` vai para a auditoria.
    """

    def __init__(self, report: SensitiveDataReport) -> None:
        super().__init__(
            "A solicitacao foi bloqueada para proteger dado sensivel.",
            status_code=422,
        )
        self.report = report


def generate_chat_response(
    request: GeminiChatRequest,
    intent: AudioIntent | None = None,
    entities: list[PublicEntity] | None = None,
    requester_id: str | None = None,
    access_context: AccessContext | None = None,
) -> GeminiChatResponse:
    api_key = _api_key()

    retrieval_started_at = perf_counter()
    secondary_intent = _resolve_secondary_safely(request, intent)
    try:
        retrieved_documents = retrieve_context(
            request.message,
            intent=intent,
            entities=entities or [],
            access_context=access_context,
        )
    except (DatabaseConfigurationError, DatabaseConnectionError) as error:
        raise GeminiAPIError(
            "Nao foi possivel recuperar contexto no banco de dados.",
            status_code=503,
        ) from error
    except RagSourceError as error:
        raise GeminiAPIError(
            "Não foi possível carregar a origem de dados configurada.",
            status_code=503,
        ) from error
    retrieval_ms = round((perf_counter() - retrieval_started_at) * 1000)

    # RNF01: o dado sensivel dos documentos e mascarado antes de montar o
    # prompt, e os classificados como restritos ficam fora do contexto. A
    # versao mascarada e a mesma usada nas fontes exibidas e na verificacao de
    # evidencia, para que a resposta continue conferivel.
    retrieved_documents, document_report = protect_documents(retrieved_documents)
    security_report = (
        document_report.audit_payload() if document_report.triggered else None
    )

    # Mesmo com o classificador desligado, nao gerar fatos sem fonte.
    if not retrieved_documents:
        return GeminiChatResponse(
            text=OUT_OF_SCOPE_ANSWER,
            model="rag-retriever",
            latency_ms=0,
            retrieval_ms=retrieval_ms,
            usage=GeminiUsage(),
            sources=[],
            evidence_status="insufficient",
            security_report=security_report,
        )

    llm = _call_llm(
        build_rag_input(
            request.message,
            retrieved_documents,
            intent=intent,
            secondary_intent=secondary_intent,
        ),
        api_key=api_key,
        previous_interaction_id=request.previous_interaction_id,
    )
    primary_text, prepared_secondary_text = _extract_prepared_responses(
        llm.text,
        secondary_intent=secondary_intent,
    )
    if secondary_intent and prepared_secondary_text is None:
        logger.warning(
            "Resposta secundaria invalida; sugestao proativa sera omitida."
        )

    public_sources = _public_sources(retrieved_documents)
    if llm.text.endswith(AVISO_RESPOSTA_INTERROMPIDA):
        # Resposta cortada pelo limite de tokens: a ultima linha esta incompleta
        # e nao pode ser verificada. O aviso, que orienta a reformular a
        # pergunta, substitui a abstencao generica.
        primary = ValidatedAnswer(AVISO_RESPOSTA_INTERROMPIDA, [], "insufficient")
        prepared_secondary_text = None
    else:
        primary = validate_evidence(primary_text, public_sources)
    if prepared_secondary_text:
        secondary = validate_evidence(
            prepared_secondary_text, public_sources, allow_recommendation=True
        )
        if secondary.status == "insufficient":
            logger.warning(
                "Resposta secundaria sem evidencia verificavel; sugestao proativa sera omitida."
            )
            prepared_secondary_text = None
        else:
            prepared_secondary_text = secondary.text
    return GeminiChatResponse(
        text=primary.text,
        claims=primary.claims,
        blocks=build_blocks(primary.claims),
        evidence_status=primary.status,
        model=llm.model,
        interaction_id=llm.interaction_id,
        latency_ms=llm.latency_ms,
        retrieval_ms=retrieval_ms,
        usage=llm.usage,
        sources=public_sources,
        trace_sources=[
            _trace_source_payload(result, citation_order=index)
            for index, result in enumerate(retrieved_documents, start=1)
        ],
        security_report=security_report,
        proactive_suggestion=(
            _public_proactive_suggestion(
                register_pending_suggestion(
                    requester_id=_required_requester_id(requester_id),
                    conversation_id=_required_conversation_id(request),
                    original_message=request.message,
                    secondary_intent=secondary_intent,
                    sources=retrieved_documents,
                    prepared_response=prepared_secondary_text,
                    prepared_model=llm.model,
                    prepared_interaction_id=llm.interaction_id,
                ),
                secondary_intent,
            )
            if secondary_intent and prepared_secondary_text and retrieved_documents
            else None
        ),
    )


@dataclass(frozen=True)
class ProactiveConfirmationExecution:
    response: ProactiveConfirmationResponse
    pending: PendingProactiveSuggestion


def execute_proactive_confirmation(
    request: ProactiveConfirmationRequest,
    *,
    requester_id: str,
) -> ProactiveConfirmationExecution:
    """Executa ou recusa a sugestao vinculada, sem aceitar texto livre."""

    if request.decision == "decline":
        pending = decline_pending_suggestion(
            request.suggestion_id,
            requester_id=requester_id,
            conversation_id=request.conversation_id,
        )
        return ProactiveConfirmationExecution(
            response=ProactiveConfirmationResponse(status="declined"),
            pending=pending,
        )

    pending = claim_pending_suggestion(
        request.suggestion_id,
        requester_id=requester_id,
        conversation_id=request.conversation_id,
    )
    result = _prepared_proactive_response(pending)

    complete_pending_suggestion(pending)
    return ProactiveConfirmationExecution(
        response=ProactiveConfirmationResponse(status="accepted", result=result),
        pending=pending,
    )


def confirm_proactive_suggestion(
    request: ProactiveConfirmationRequest,
    *,
    requester_id: str,
) -> ProactiveConfirmationResponse:
    """Atalho sem contexto de auditoria, mantido para os testes do cliente."""

    return execute_proactive_confirmation(
        request,
        requester_id=requester_id,
    ).response


def _prepared_proactive_response(
    pending: PendingProactiveSuggestion,
) -> GeminiChatResponse:
    if not pending.prepared_response:
        raise GeminiAPIError(
            "A sugestao nao possui resposta preparada.",
            status_code=409,
        )
    public_sources = _public_sources(pending.sources)
    prepared = validate_evidence(
        pending.prepared_response, public_sources, allow_recommendation=True
    )
    return GeminiChatResponse(
        text=prepared.text,
        claims=prepared.claims,
        blocks=build_blocks(prepared.claims),
        evidence_status=prepared.status,
        recommendation=prepared.recommendation,
        model=pending.prepared_model or "resposta-preparada",
        interaction_id=pending.prepared_interaction_id,
        latency_ms=0,
        usage=GeminiUsage(),
        sources=public_sources,
        trace_sources=[
            _trace_source_payload(result, citation_order=index)
            for index, result in enumerate(pending.sources, start=1)
        ],
    )


def _extract_prepared_responses(
    text: str,
    *,
    secondary_intent: SecondaryIntent | None,
) -> tuple[str, str | None]:
    if secondary_intent is None:
        return text, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text, None
    if not isinstance(payload, dict):
        return text, None
    primary = payload.get("primary_response")
    prepared = payload.get("prepared_secondary_response")
    if not isinstance(primary, str) or not primary.strip():
        return text, None
    if not isinstance(prepared, str) or not prepared.strip():
        return primary.strip(), None
    return primary.strip(), prepared.strip()


@dataclass(frozen=True)
class _LLMResult:
    """Resposta do provedor ja normalizada, independente de quem a produziu."""

    text: str
    model: str
    interaction_id: str | None
    latency_ms: int
    usage: GeminiUsage


def _provider() -> str:
    """Provedor configurado em `LLM_PROVIDER`; Gemini direto quando ausente.

    Valor desconhecido e erro de configuracao, nao queda silenciosa para o
    padrao: um `LLM_PROVIDER=openrotuer` que caisse no Gemini sem avisar faria a
    equipe medir um provedor achando que mede outro.
    """

    value = os.getenv("LLM_PROVIDER", LLM_PROVIDER_GEMINI).strip().lower()
    if value not in VALID_LLM_PROVIDERS:
        raise GeminiConfigurationError(
            f"LLM_PROVIDER invalido: use {', '.join(sorted(VALID_LLM_PROVIDERS))}."
        )
    return value


def _api_key() -> str:
    name = (
        "OPENROUTER_API_KEY"
        if _provider() == LLM_PROVIDER_OPENROUTER
        else "GEMINI_API_KEY"
    )
    api_key = os.getenv(name, "").strip()
    if not api_key:
        raise GeminiConfigurationError(
            f"A chave {name} nao foi configurada no backend."
        )
    return api_key


def _call_llm(
    prompt: str,
    *,
    api_key: str,
    previous_interaction_id: str | None = None,
) -> _LLMResult:
    """Unico ponto de chamada ao LLM, compartilhado pelas duas rotas do cliente."""

    # Guarda final do RNF01: nenhum prompt com dado sensivel sai daqui, mesmo
    # que um caminho futuro esqueca as barreiras da pergunta e dos documentos.
    guard = scan(prompt)
    if guard.found:
        logger.warning(
            "Chamada ao provedor bloqueada: dado sensivel no prompt (%s).",
            ", ".join(guard.categories),
        )
        raise SensitiveDataBlockedError(
            SensitiveDataReport(stage="prompt", action="bloqueado", counts=guard.counts)
        )

    if _provider() == LLM_PROVIDER_OPENROUTER:
        return _call_openrouter(prompt, api_key=api_key)
    return _call_gemini(
        prompt,
        api_key=api_key,
        previous_interaction_id=previous_interaction_id,
    )


def _call_gemini(
    prompt: str,
    *,
    api_key: str,
    previous_interaction_id: str | None,
) -> _LLMResult:
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    payload: dict[str, object] = {
        "model": model,
        "input": prompt,
        "store": True,
        "generation_config": {
            "max_output_tokens": _max_output_tokens(),
            "thinking_level": _thinking_level(),
        },
    }
    if previous_interaction_id:
        payload["previous_interaction_id"] = previous_interaction_id

    http_request = Request(
        GEMINI_INTERACTIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    started_at = perf_counter()
    response_data = _send_request_with_retry(http_request)
    latency_ms = round((perf_counter() - started_at) * 1000)

    text = _extract_text(response_data)
    if not text:
        raise GeminiAPIError("O Gemini nao retornou conteudo de texto.")

    usage_data = response_data.get("usage", {})
    return _LLMResult(
        text=text,
        model=str(response_data.get("model") or model),
        interaction_id=response_data.get("id"),
        latency_ms=latency_ms,
        usage=GeminiUsage(
            input_tokens=_as_int(usage_data.get("total_input_tokens")),
            output_tokens=_as_int(usage_data.get("total_output_tokens")),
            thought_tokens=_as_int(usage_data.get("total_thought_tokens")),
            total_tokens=_as_int(usage_data.get("total_tokens")),
        ),
    )


def _call_openrouter(prompt: str, *, api_key: str) -> _LLMResult:
    """Chama o modelo pelo endpoint compativel com OpenAI do OpenRouter.

    Diferencas em relacao ao Gemini direto, todas deliberadas:

    - o prompt vai inteiro como uma mensagem de usuario, exatamente o mesmo
      texto que o Gemini recebe em `input`, para que trocar de provedor nao mude
      o que o modelo le;
    - `thinking_level` vira `reasoning.effort`, que e como o OpenRouter expoe o
      mesmo controle;
    - **nao ha continuidade de conversa.** O OpenRouter nao guarda estado entre
      chamadas, entao `previous_interaction_id` nao tem equivalente e e
      ignorado. Cada pergunta e respondida sem o historico. E uma limitacao
      real deste provedor e precisa ser considerada antes de adota-lo no MVP.
    """

    model = (
        os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL).strip()
        or DEFAULT_OPENROUTER_MODEL
    )
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": _max_output_tokens(),
        "reasoning": {"effort": _thinking_level()},
    }
    http_request = Request(
        OPENROUTER_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Title": "Oneshot - Agente de Portfolio do Metro",
        },
        method="POST",
    )
    started_at = perf_counter()
    response_data = _send_request_with_retry(http_request)
    latency_ms = round((perf_counter() - started_at) * 1000)

    text = _extract_openrouter_text(response_data)

    # Os tokens de raciocinio consomem o mesmo `max_tokens` do texto visivel:
    # numa chamada medida, 245 dos 287 tokens de saida foram raciocinio. Quando
    # o modelo raciocina demais, a resposta e cortada no meio da frase ou chega
    # vazia. Na rodada do RNF04, duas respostas cortadas foram entregues como
    # completas; no teste de usabilidade, uma chegou so com o aviso de dados
    # ficticios. A resposta cortada passa a vir acompanhada de um aviso ao
    # usuario, e a vazia e substituida por ele, em vez de virar erro.
    choices = response_data.get("choices") or [{}]
    if choices[0].get("finish_reason") == "length":
        logger.warning(
            "Resposta do LLM truncada pelo limite de %d tokens (modelo %s).",
            _max_output_tokens(),
            model,
        )
        text = (
            f"{text}\n\n{AVISO_RESPOSTA_INTERROMPIDA}"
            if text
            else AVISO_RESPOSTA_INTERROMPIDA
        )
    if not text:
        raise GeminiAPIError("O provedor nao retornou conteudo de texto.")

    usage_data = response_data.get("usage") or {}
    detalhes = usage_data.get("completion_tokens_details") or {}
    return _LLMResult(
        text=text,
        model=str(response_data.get("model") or model),
        interaction_id=response_data.get("id"),
        latency_ms=latency_ms,
        usage=GeminiUsage(
            input_tokens=_as_int(usage_data.get("prompt_tokens")),
            output_tokens=_as_int(usage_data.get("completion_tokens")),
            thought_tokens=_as_int(detalhes.get("reasoning_tokens")),
            total_tokens=_as_int(usage_data.get("total_tokens")),
        ),
    )


def _extract_openrouter_text(response_data: dict) -> str:
    """Le `choices[0].message.content`, em texto simples ou em partes."""

    choices = response_data.get("choices") or []
    if not choices:
        return ""
    content = (choices[0].get("message") or {}).get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        partes = [
            parte.get("text", "").strip()
            for parte in content
            if isinstance(parte, dict) and parte.get("type") == "text"
        ]
        return "\n\n".join(parte for parte in partes if parte)
    return ""


def _extract_text(response_data: dict) -> str:
    texts: list[str] = []
    for step in response_data.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for content in step.get("content", []):
            text = content.get("text") if content.get("type") == "text" else None
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
    return "\n\n".join(texts)


def _read_api_error(error: HTTPError) -> str:
    try:
        body = json.loads(error.read().decode("utf-8"))
        message = body.get("error", {}).get("message")
        if isinstance(message, str) and message.strip():
            return message
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return "O Gemini recusou a requisicao. Verifique a chave e o modelo configurados."


def _send_request_with_retry(http_request: Request) -> dict:
    max_retries = _max_retries()

    for attempt in range(max_retries + 1):
        try:
            with urlopen(http_request, timeout=_request_timeout_seconds()) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code in RETRYABLE_HTTP_STATUS_CODES and attempt < max_retries:
                _log_retry(f"HTTP {error.code}", attempt, max_retries)
                sleep(_retry_delay_seconds(attempt))
                continue

            message = _read_api_error(error)
            status_code = 429 if error.code == 429 else 502
            raise GeminiAPIError(message, status_code=status_code) from error
        except (URLError, TimeoutError) as error:
            if attempt < max_retries:
                _log_retry(type(error).__name__, attempt, max_retries)
                sleep(_retry_delay_seconds(attempt))
                continue

            raise GeminiAPIError(
                "Nao foi possivel conectar ao Gemini. Tente novamente em instantes."
            ) from error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise GeminiAPIError("O Gemini retornou uma resposta invalida.") from error

    raise GeminiAPIError("Nao foi possivel conectar ao Gemini.")


def _log_retry(motivo: str, attempt: int, max_retries: int) -> None:
    """Registra cada nova tentativa contra o provedor.

    Sem este registro, um travamento do provedor e invisivel: a requisicao so
    demora mais. Na rodada do RNF05 de 22/09/2026, uma consulta levou 37,7 s —
    valor que bate com o timeout de 30 s, mais 2 s de espera e uma nova
    tentativa, mas que nao pode ser confirmado porque nada foi registrado.
    """

    logger.warning(
        "Chamada ao provedor do LLM falhou (%s); tentativa %d de %d em %.1f s.",
        motivo,
        attempt + 2,
        max_retries + 1,
        _retry_delay_seconds(attempt),
    )


def _max_output_tokens() -> int:
    raw_value = os.getenv(
        "GEMINI_MAX_OUTPUT_TOKENS", str(DEFAULT_MAX_OUTPUT_TOKENS)
    )
    try:
        return min(max(int(raw_value), 64), 8192)
    except ValueError:
        return DEFAULT_MAX_OUTPUT_TOKENS


def _thinking_level() -> str:
    value = os.getenv("GEMINI_THINKING_LEVEL", "low").strip().lower()
    return value if value in VALID_THINKING_LEVELS else "low"


def _request_timeout_seconds() -> int:
    return _bounded_int_env(
        "GEMINI_REQUEST_TIMEOUT_SECONDS",
        default=DEFAULT_REQUEST_TIMEOUT_SECONDS,
        minimum=1,
        maximum=120,
    )


def _max_retries() -> int:
    return _bounded_int_env(
        "GEMINI_MAX_RETRIES",
        default=DEFAULT_MAX_RETRIES,
        minimum=0,
        maximum=6,
    )


def _retry_delay_seconds(attempt: int) -> float:
    raw_value = os.getenv(
        "GEMINI_RETRY_BASE_DELAY_SECONDS",
        str(DEFAULT_RETRY_BASE_DELAY_SECONDS),
    )
    try:
        base_delay = min(max(float(raw_value), 0.0), 60.0)
    except ValueError:
        base_delay = DEFAULT_RETRY_BASE_DELAY_SECONDS
    return base_delay * (2**attempt)


def _bounded_int_env(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        return min(max(int(os.getenv(name, str(default))), minimum), maximum)
    except ValueError:
        return default


def _as_int(value: object) -> int:
    return value if isinstance(value, int) else 0


def _resolve_secondary_safely(
    request: GeminiChatRequest,
    intent: AudioIntent | None,
) -> SecondaryIntent | None:
    if not request.proactivity_enabled:
        return None
    try:
        return resolve_secondary_intent(intent)
    except (DatabaseConfigurationError, DatabaseConnectionError):
        logger.warning(
            "Intencao secundaria indisponivel; resposta primaria sera preservada."
        )
        return None


def _required_requester_id(requester_id: str | None) -> str:
    if not requester_id:
        raise GeminiAPIError(
            "A proatividade exige uma identidade autenticada.",
            status_code=401,
        )
    return requester_id


def _required_conversation_id(request: GeminiChatRequest) -> str:
    if not request.conversation_id:
        raise GeminiAPIError(
            "A proatividade exige uma conversa identificada.",
            status_code=422,
        )
    return request.conversation_id


def _public_proactive_suggestion(
    suggestion_id: str,
    secondary_intent: SecondaryIntent,
) -> ProactiveSuggestion:
    return ProactiveSuggestion(
        suggestion_id=suggestion_id,
        intent=secondary_intent.name,
        description=secondary_intent.description,
        display_message=secondary_intent.display_message,
    )


def _public_sources(results) -> list[GeminiSource]:
    return [
        GeminiSource(
            id=result.document.source_id,
            title=result.document.title,
            list_name=result.document.list_name,
            web_url=result.document.web_url,
            last_modified=result.document.last_modified,
            score=result.score,
            excerpt=result.document.content,
            citation_id=f"Fonte {index}",
            artifact_id=result.document.artifact_id,
            extract_id=result.document.extract_id,
            project_id=result.document.project_id,
            source_locator=result.document.source_locator,
            registration_period=result.document.registration_period,
            validity=result.document.validity,
            attributes=dict(result.document.attributes),
        )
        for index, result in enumerate(results, start=1)
    ]


def _trace_source_payload(result: object, citation_order: int) -> dict:
    document = result.document
    return {
        "artifact_id": document.artifact_id,
        "extract_id": document.extract_id,
        "project_id": document.project_id,
        "source_type": "lista_sharepoint",
        "source_title": document.title,
        "source_url": document.web_url,
        "source_locator": document.source_locator,
        "relevance_score": min(max(float(result.score or 0) / 10, 0), 1),
        "citation_order": citation_order,
        "metadata": {
            "fallback": document.fallback,
            "source_id": document.source_id,
            "list_name": document.list_name,
            "citation_id": f"Fonte {citation_order}",
            "excerpt": document.content,
            "last_modified": document.last_modified,
            "registration_period": document.registration_period,
            "validity": document.validity,
            "attributes": dict(document.attributes),
        },
    }
