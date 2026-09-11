import json
import os
from time import perf_counter, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.gemini.schemas import (
    GeminiChatRequest,
    GeminiChatResponse,
    GeminiSource,
    GeminiUsage,
)
from app.database.connection import DatabaseConfigurationError, DatabaseConnectionError
from app.nlp.schemas import AudioIntent, PublicEntity
from app.rag.database import retrieve_context
from app.rag.sharepoint import build_rag_input

GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_MAX_OUTPUT_TOKENS = 512
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_DELAY_SECONDS = 2.0
RETRYABLE_HTTP_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
VALID_THINKING_LEVELS = frozenset({"minimal", "low", "medium", "high"})


class GeminiConfigurationError(RuntimeError):
    pass


class GeminiAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def generate_chat_response(
    request: GeminiChatRequest,
    intent: AudioIntent | None = None,
    entities: list[PublicEntity] | None = None,
) -> GeminiChatResponse:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiConfigurationError(
            "A chave GEMINI_API_KEY nao foi configurada no backend."
        )

    retrieval_started_at = perf_counter()
    try:
        retrieved_documents = retrieve_context(
            request.message,
            intent=intent,
            entities=entities or [],
        )
    except (DatabaseConfigurationError, DatabaseConnectionError) as error:
        raise GeminiAPIError(
            "Nao foi possivel recuperar contexto no banco de dados.",
            status_code=503,
        ) from error
    retrieval_ms = round((perf_counter() - retrieval_started_at) * 1000)

    if _requires_context(intent) and not retrieved_documents:
        return GeminiChatResponse(
            text=(
                "Nao encontrei fontes suficientes para responder com seguranca. "
                "Informe outro projeto, linha ou criterio de consulta."
            ),
            model="rag-retriever",
            latency_ms=0,
            retrieval_ms=retrieval_ms,
            usage=GeminiUsage(),
            sources=[],
        )

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    payload: dict[str, object] = {
        "model": model,
        "input": build_rag_input(request.message, retrieved_documents),
        "store": True,
        "generation_config": {
            "max_output_tokens": _max_output_tokens(),
            "thinking_level": _thinking_level(),
        },
    }
    if request.previous_interaction_id:
        payload["previous_interaction_id"] = request.previous_interaction_id

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
    return GeminiChatResponse(
        text=text,
        model=str(response_data.get("model") or model),
        interaction_id=response_data.get("id"),
        latency_ms=latency_ms,
        retrieval_ms=retrieval_ms,
        usage=GeminiUsage(
            input_tokens=_as_int(usage_data.get("total_input_tokens")),
            output_tokens=_as_int(usage_data.get("total_output_tokens")),
            thought_tokens=_as_int(usage_data.get("total_thought_tokens")),
            total_tokens=_as_int(usage_data.get("total_tokens")),
        ),
        sources=[
            GeminiSource(
                id=result.document.source_id,
                title=result.document.title,
                list_name=result.document.list_name,
                web_url=result.document.web_url,
                last_modified=result.document.last_modified,
                score=result.score,
                excerpt=result.document.content,
            )
            for result in retrieved_documents
        ],
        trace_sources=[
            _trace_source_payload(result, citation_order=index)
            for index, result in enumerate(retrieved_documents, start=1)
        ],
    )


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
                sleep(_retry_delay_seconds(attempt))
                continue

            message = _read_api_error(error)
            status_code = 429 if error.code == 429 else 502
            raise GeminiAPIError(message, status_code=status_code) from error
        except (URLError, TimeoutError) as error:
            if attempt < max_retries:
                sleep(_retry_delay_seconds(attempt))
                continue

            raise GeminiAPIError(
                "Nao foi possivel conectar ao Gemini. Tente novamente em instantes."
            ) from error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise GeminiAPIError("O Gemini retornou uma resposta invalida.") from error

    raise GeminiAPIError("Nao foi possivel conectar ao Gemini.")


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


def _requires_context(intent: AudioIntent | None) -> bool:
    return bool(intent and intent.macro == "CONSULTA" and intent.specific)


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
        },
    }
