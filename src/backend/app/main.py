import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.audio.errors import AudioError, AudioMissingError, AudioTooLargeError
from app.audio.schemas import (
    AudioAnswer,
    AudioAnswerSource,
    AudioErrorResponse,
    AudioUploadResponse,
)
from app.audio.security import resolve_identity, single_request_per_identity
from app.audio.service import process_audio_upload
from app.audio.validation import DEFAULT_MAX_SIZE_BYTES
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
)
from app.gemini.schemas import (
    GeminiChatRequest,
    GeminiChatResponse,
    ProactiveConfirmationRequest,
    ProactiveConfirmationResponse,
)
from app.nlp.schemas import AudioPipelineMetrics
from app.pipeline import (
    process_message,
    process_proactive_confirmation,
    warmup_classifier,
)
from app.rag.proactive_confirmation import (
    PendingSuggestionInProgress,
    PendingSuggestionNotFound,
    PendingSuggestionStorageError,
)
from app.reports.errors import ReportError
from app.reports.router import router as reports_router

# Container and process environment is authoritative. A local .env remains a
# development convenience, but must not replace variables injected at runtime.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

AUDIO_PATH = "/api/audio"
DEFAULT_LANGUAGE = "pt-BR"
UPLOAD_CHUNK_SIZE = 64 * 1024

AUDIO_ERROR_RESPONSES: dict[int | str, dict] = {
    status: {"model": AudioErrorResponse, "description": description}
    for status, description in {
        400: "Audio ausente, em formato nao suportado ou acima da duracao maxima.",
        401: "Token ausente, invalido ou expirado.",
        413: "Arquivo acima do limite de tamanho.",
        422: "Audio valido, porem sem fala reconhecivel.",
        429: "Ja existe uma transcricao em andamento para o usuario.",
        502: "Falha na chamada ao servico de transcricao.",
        503: "Servico de transcricao indisponivel.",
    }.items()
}

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.getenv("PLN_WARMUP", "0") == "1":
        await run_in_threadpool(warmup_classifier)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="API de IA do Metro",
    description="Chat via Gemini com recuperacao de contexto em listas simuladas do SharePoint.",
    version="0.1.0",
)
app.include_router(reports_router)


@app.exception_handler(AudioError)
def handle_audio_error(_request: Request, error: AudioError) -> JSONResponse:
    """Converte os cenarios previstos no envelope unico da Secao 8.7.6."""

    return JSONResponse(status_code=error.status_code, content=error.to_payload())


@app.exception_handler(ReportError)
def handle_report_error(_request: Request, error: ReportError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"error": {"code": error.code, "message": error.message}},
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request, error: RequestValidationError
):
    """Impede que o detalhamento de validacao do FastAPI chegue ao usuario.

    O corpo padrao expoe caminho de campo e tipo interno esperado, o que o
    RNF11 nao admite na resposta ao usuario final. Na rota de audio a falha e
    reescrita como `AUDIO_MISSING`, unico caso possivel de corpo invalido no
    contrato multipart; as demais rotas mantem o comportamento padrao.
    """

    if request.url.path == "/api/chat/proactive-confirmation":
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": (
                        "Informe uma sugestão válida e uma decisão de aceitar "
                        "ou recusar."
                    ),
                }
            },
        )
    if request.url.path == "/api/chat":
        return JSONResponse(status_code=422, content={"error": {"code": "INVALID_INPUT", "message": "Informe uma mensagem de 1 a 20.000 caracteres e parâmetros válidos."}})
    if (
        request.url.path.startswith("/api/report-requests")
        or request.url.path.startswith("/api/workflow-sessions")
        or request.url.path.startswith(
            "/api/integrations/power-automate/report-results"
        )
    ):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "REPORT_INVALID_INPUT",
                    "message": "Revise os parametros informados para o relatorio.",
                }
            },
        )
    if request.url.path != AUDIO_PATH:
        return await request_validation_exception_handler(request, error)

    if any(item["loc"][-1] != "audio" for item in error.errors()):
        return JSONResponse(status_code=400, content={"error": {"code": "INVALID_INPUT", "message": "Confira os parâmetros enviados com o áudio."}})

    missing = AudioMissingError()
    return JSONResponse(status_code=missing.status_code, content=missing.to_payload())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=GeminiChatResponse)
def create_chat_response(
    request: GeminiChatRequest,
    authorization: str | None = Header(default=None),
) -> GeminiChatResponse:
    try:
        identity = (
            resolve_identity(authorization)
            if authorization or request.proactivity_enabled
            else None
        )
        return process_message(
            request,
            requester_id=identity.object_id if identity else None,
        )
    except GeminiConfigurationError as error:
        raise HTTPException(status_code=503, detail="O serviço de processamento está indisponível. Tente novamente em instantes.") from error
    except GeminiAPIError as error:
        raise HTTPException(status_code=error.status_code, detail="Não foi possível obter uma resposta. Tente novamente em instantes.") from error
    except PendingSuggestionStorageError as error:
        raise HTTPException(
            status_code=503,
            detail="O armazenamento de confirmações está indisponível.",
        ) from error


@app.post(
    "/api/chat/proactive-confirmation",
    response_model=ProactiveConfirmationResponse,
)
def create_proactive_confirmation(
    request: ProactiveConfirmationRequest,
    authorization: str | None = Header(default=None),
) -> ProactiveConfirmationResponse:
    try:
        identity = resolve_identity(authorization)
        return process_proactive_confirmation(
            request,
            requester_id=identity.object_id,
        )
    except PendingSuggestionNotFound as error:
        raise HTTPException(
            status_code=404,
            detail="A sugestão expirou ou já recebeu uma decisão.",
        ) from error
    except PendingSuggestionInProgress as error:
        raise HTTPException(
            status_code=409,
            detail="A sugestão já está sendo processada.",
        ) from error
    except PendingSuggestionStorageError as error:
        raise HTTPException(
            status_code=503,
            detail="O armazenamento de confirmações está indisponível.",
        ) from error
    except GeminiConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail="O serviço de processamento está indisponível. Tente novamente em instantes.",
        ) from error
    except GeminiAPIError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail="Não foi possível executar a sugestão. Tente novamente em instantes.",
        ) from error


@app.post(
    AUDIO_PATH,
    response_model=AudioUploadResponse,
    responses=AUDIO_ERROR_RESPONSES,
    summary="Enviar audio para transcricao e processamento",
)
async def create_audio_upload(
    audio: UploadFile | None = File(default=None),
    conversation_id: str | None = Form(default=None),
    language: str | None = Form(default=None),
    previous_interaction_id: str | None = Form(default=None, max_length=1024),
    use_intent_classifier: bool = Form(default=True),
    proactivity_enabled: bool = Form(default=False),
    authorization: str | None = Header(default=None),
) -> AudioUploadResponse:
    started_at = perf_counter()
    identity = resolve_identity(authorization)
    resolved_conversation_id = conversation_id or str(uuid4())

    if audio is None:
        raise AudioMissingError()

    with single_request_per_identity(identity):
        data = await _read_upload(audio)
        if not data:
            raise AudioMissingError()

        audio_result = await process_audio_upload(
            data,
            language=language or DEFAULT_LANGUAGE,
        )
        response = await run_in_threadpool(
            process_message,
            GeminiChatRequest(
                message=audio_result.transcription.text,
                conversation_id=resolved_conversation_id,
                previous_interaction_id=previous_interaction_id,
                use_intent_classifier=use_intent_classifier,
                proactivity_enabled=proactivity_enabled,
            ),
            requester_id=identity.object_id,
        )
        return AudioUploadResponse(
            conversation_id=resolved_conversation_id,
            interaction_id=response.interaction_id,
            transcription=audio_result.transcription,
            intent=response.intent,
            entities=response.entities,
            answer=AudioAnswer(text=response.text, sources=[
                AudioAnswerSource(artifact=source.title, section=source.list_name)
                for source in response.sources
            ]),
            chat=response,
            pipeline_status="completed",
            pipeline_metrics=AudioPipelineMetrics(
                validation_ms=audio_result.validation_ms,
                stt_ms=audio_result.stt_ms,
                nlp_ms=response.pipeline_metrics.nlp_ms,
                route_ms=response.pipeline_metrics.route_ms,
                total_ms=round((perf_counter() - started_at) * 1000),
            ),
        )


async def _read_upload(audio: UploadFile) -> bytes:
    """Le o arquivo em blocos e interrompe assim que o limite e ultrapassado.

    Ler o upload inteiro antes de comparar com o teto de 2 MB faria a API
    carregar em memoria um arquivo que ela ja iria recusar. O corte acontece um
    byte alem do limite, apenas para diferenciar o arquivo no limite do arquivo
    acima dele.
    """

    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await audio.read(UPLOAD_CHUNK_SIZE)
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > DEFAULT_MAX_SIZE_BYTES:
            raise AudioTooLargeError(DEFAULT_MAX_SIZE_BYTES)

    return b"".join(chunks)
