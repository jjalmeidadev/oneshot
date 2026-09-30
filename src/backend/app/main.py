import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from starlette.concurrency import run_in_threadpool

from app.audio.errors import (
    AudioError,
    AudioMissingError,
    AudioTooLargeError,
    ProcessingProviderFailedError,
    ProcessingUnavailableError,
)
from app.audio.schemas import (
    MAX_CONVERSATION_ID_LENGTH,
    AudioAnswer,
    AudioAnswerSource,
    AudioErrorResponse,
    AudioUploadResponse,
    VhsMetricsResponse,
)
from app.audio import transcription
from app.audio.security import single_request_per_identity
from app.audio.service import process_audio_upload
from app.audio.validation import DEFAULT_MAX_SIZE_BYTES
from app.database.connection import close_database_pool
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
from app.alerts.errors import AlertError
from app.alerts.router import router as alerts_router
from app.security import (
    AccessContext,
    AccessError,
    AccessProfileResponse,
    PasswordLoginRequest,
    PasswordLoginResponse,
    OutOfScopeForProfileError,
    audit_request_denial,
    access_profile_from_context,
    authenticate_persona,
    authorize_message_scope,
    get_access_context,
    require_read_access,
    require_write_access,
)

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
    await run_in_threadpool(close_database_pool)


app = FastAPI(
    lifespan=lifespan,
    title="API de IA do Metro",
    description="Chat via Gemini com recuperacao de contexto em listas simuladas do SharePoint.",
    version="0.1.0",
)
app.include_router(reports_router)
app.include_router(alerts_router)
ReadAccess = Annotated[AccessContext, Depends(require_read_access)]
WriteAccess = Annotated[AccessContext, Depends(require_write_access)]
AuthenticatedAccess = Annotated[AccessContext, Depends(get_access_context)]


@app.exception_handler(AudioError)
def handle_audio_error(_request: Request, error: AudioError) -> JSONResponse:
    """Converte os cenarios previstos no envelope unico da Secao 8.7.6."""

    return JSONResponse(status_code=error.status_code, content=error.to_payload())


@app.exception_handler(ReportError)
def handle_report_error(_request: Request, error: ReportError) -> JSONResponse:
    if error.status_code == 403:
        audit_request_denial(_request)
    return JSONResponse(
        status_code=error.status_code,
        content={"error": {"code": error.code, "message": error.message}},
    )


@app.exception_handler(AlertError)
def handle_alert_error(_request: Request, error: AlertError) -> JSONResponse:
    if error.status_code == 403:
        audit_request_denial(_request)
    return JSONResponse(
        status_code=error.status_code,
        content={"error": {"code": error.code, "message": error.message}},
    )


@app.exception_handler(AccessError)
def handle_access_error(_request: Request, error: AccessError) -> JSONResponse:
    """Preserva codigos publicos estaveis sem expor detalhes de Auth ou banco."""

    if isinstance(error, OutOfScopeForProfileError):
        audit_request_denial(_request, error)
    return JSONResponse(status_code=error.status_code, content=error.to_payload())


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
    if request.url.path == "/api/access/login":
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Selecione uma persona e informe a senha.",
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
    if (
        request.url.path.startswith("/api/alert-")
        or request.url.path.startswith("/api/notifications")
        or request.url.path.startswith(
            "/api/integrations/notifications/delivery-results"
        )
    ):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "ALERT_INVALID_INPUT",
                    "message": "Revise os parametros informados para o alerta.",
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


@app.get("/api/access/me", response_model=AccessProfileResponse)
def get_current_access_profile(
    access: AuthenticatedAccess,
) -> AccessProfileResponse:
    """Retorna somente a identidade de exibicao e o resumo de acesso atual."""

    return access_profile_from_context(access)


@app.post("/api/access/login", response_model=PasswordLoginResponse)
def login_with_password(
    credentials: PasswordLoginRequest,
    response: Response,
) -> PasswordLoginResponse:
    """Autentica uma das quatro contas sintéticas sem expor e-mail no cliente."""

    response.headers["Cache-Control"] = "no-store"
    return authenticate_persona(credentials.profile_key, credentials.password)


@app.get("/api/audio/vhs/metrics", response_model=VhsMetricsResponse)
def get_vhs_metrics(
    access: ReadAccess,
) -> VhsMetricsResponse:
    """Expõe somente contadores agregados a uma identidade autenticada."""

    snapshot = transcription.response_cache.snapshot()
    return VhsMetricsResponse(
        enabled=os.getenv("VHS_ENABLED", "1").strip() != "0",
        worker_id=transcription.VHS_WORKER_ID,
        **snapshot,
    )


@app.post("/api/chat", response_model=GeminiChatResponse)
def create_chat_response(
    request: GeminiChatRequest,
    access: ReadAccess,
) -> GeminiChatResponse:
    try:
        authorize_message_scope(access, request.message)
        return process_message(
            request,
            requester_id=str(access.auth_subject),
            user_id=str(access.user_id),
            access_context=access,
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
    access: WriteAccess,
) -> ProactiveConfirmationResponse:
    try:
        return process_proactive_confirmation(
            request,
            requester_id=str(access.auth_subject),
            user_id=str(access.user_id),
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


def create_audio_chat_response(
    request: GeminiChatRequest,
    conversation_id: str,
    access_context: AccessContext,
) -> GeminiChatResponse:
    """Executa o pipeline comum preservando o envelope de erro da rota de audio."""

    try:
        authorize_message_scope(access_context, request.message)
        return process_message(
            request,
            channel="api",
            external_conversation_id=conversation_id,
            requester_id=str(access_context.auth_subject),
            user_id=str(access_context.user_id),
            access_context=access_context,
        )
    except GeminiConfigurationError as error:
        raise ProcessingUnavailableError() from error
    except GeminiAPIError as error:
        raise ProcessingProviderFailedError() from error


@app.post(
    AUDIO_PATH,
    response_model=AudioUploadResponse,
    responses=AUDIO_ERROR_RESPONSES,
    summary="Enviar audio para transcricao e processamento",
)
async def create_audio_upload(
    access: ReadAccess,
    audio: UploadFile | None = File(default=None),
    conversation_id: str | None = Form(
        default=None,
        max_length=MAX_CONVERSATION_ID_LENGTH,
    ),
    language: str | None = Form(default=None),
    previous_interaction_id: str | None = Form(default=None, max_length=1024),
    use_intent_classifier: bool = Form(default=True),
    proactivity_enabled: bool = Form(default=False),
) -> AudioUploadResponse:
    started_at = perf_counter()
    resolved_conversation_id = conversation_id or str(uuid4())

    if audio is None:
        raise AudioMissingError()

    with single_request_per_identity(access.user_id):
        data = await _read_upload(audio)
        if not data:
            raise AudioMissingError()

        audio_result = await process_audio_upload(
            data,
            language=language or DEFAULT_LANGUAGE,
        )
        response = await run_in_threadpool(
            create_audio_chat_response,
            GeminiChatRequest(
                message=audio_result.transcription.text,
                conversation_id=resolved_conversation_id,
                previous_interaction_id=previous_interaction_id,
                use_intent_classifier=use_intent_classifier,
                proactivity_enabled=proactivity_enabled,
            ),
            resolved_conversation_id,
            access,
        )
        return AudioUploadResponse(
            conversation_id=resolved_conversation_id,
            interaction_id=response.interaction_id,
            trace_id=response.trace_id,
            transcription=audio_result.transcription,
            intent=response.intent,
            entities=response.entities,
            answer=AudioAnswer(text=response.text, claims=response.claims,
                evidence_status=response.evidence_status, sources=[
                AudioAnswerSource(**source.model_dump(), artifact=source.title,
                                  section=source.source_locator or source.list_name)
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
