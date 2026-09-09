from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.audio.errors import AudioError, AudioMissingError, AudioTooLargeError
from app.audio.schemas import AudioErrorResponse, AudioUploadResponse
from app.audio.security import resolve_identity, single_request_per_identity
from app.audio.service import process_audio_upload
from app.audio.validation import DEFAULT_MAX_SIZE_BYTES
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    generate_chat_response,
)
from app.gemini.schemas import (
    ChatEntity,
    ChatIntent,
    ChatIntentAlternative,
    ChatPipelineMetrics,
    GeminiChatRequest,
    GeminiChatResponse,
    GeminiUsage,
)
from app.nlp.entities import Entidade
from app.nlp.inference import Classificacao
from app.nlp.pipeline import NlpPipelineResult, process_text_pipeline


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

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

app = FastAPI(
    title="API de IA do Metro",
    description="Chat via Gemini com recuperacao de contexto em listas simuladas do SharePoint.",
    version="0.1.0",
)


@app.exception_handler(AudioError)
def handle_audio_error(_request: Request, error: AudioError) -> JSONResponse:
    """Converte os cenarios previstos no envelope unico da Secao 8.7.6."""

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

    if request.url.path != AUDIO_PATH:
        return await request_validation_exception_handler(request, error)

    missing = AudioMissingError()
    return JSONResponse(status_code=missing.status_code, content=missing.to_payload())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=GeminiChatResponse)
def create_chat_response(request: GeminiChatRequest) -> GeminiChatResponse:
    route_started_at = perf_counter()
    pipeline = process_text_pipeline(request.message)
    if pipeline.blocked:
        return _controlled_chat_response(
            text=pipeline.controlled_answer,
            pipeline=pipeline,
            route_started_at=route_started_at,
        )

    try:
        response = generate_chat_response(request)
    except GeminiConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except GeminiAPIError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error

    response.intent = _serialize_intent(pipeline.classification)
    response.entities = _serialize_entities(pipeline.entities)
    response.pipeline_metrics = ChatPipelineMetrics(
        nlp_ms=pipeline.nlp_ms,
        route_ms=_elapsed_ms(route_started_at),
    )
    return response


def _controlled_chat_response(
    *,
    text: str | None,
    pipeline: NlpPipelineResult,
    route_started_at: float,
) -> GeminiChatResponse:
    return GeminiChatResponse(
        text=text or "",
        model="pln-router",
        interaction_id=None,
        latency_ms=0,
        retrieval_ms=0,
        usage=GeminiUsage(),
        sources=[],
        intent=_serialize_intent(pipeline.classification),
        entities=_serialize_entities(pipeline.entities),
        pipeline_metrics=ChatPipelineMetrics(
            nlp_ms=pipeline.nlp_ms,
            route_ms=_elapsed_ms(route_started_at),
        ),
    )


def _serialize_intent(classification: Classificacao) -> ChatIntent:
    return ChatIntent(
        macro=classification.macrointencao,
        specific=classification.intencao,
        confidence_macro=classification.confianca_macro,
        confidence_specific=classification.confianca_intencao,
        flow=classification.fluxo,
        handler=classification.handler,
        alternatives=[
            ChatIntentAlternative(intent=intent, confidence=confidence)
            for intent, confidence in classification.alternativas
        ],
    )


def _serialize_entities(entities: list[Entidade]) -> list[ChatEntity]:
    return [
        ChatEntity(
            type=entity.tipo,
            value=entity.valor,
            text=entity.texto,
            start=entity.inicio,
            end=entity.fim,
            types=list(entity.tipos),
            ambiguous=entity.ambigua,
        )
        for entity in entities
    ]


def _elapsed_ms(started_at: float) -> int:
    return round((perf_counter() - started_at) * 1000)


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
    authorization: str | None = Header(default=None),
) -> AudioUploadResponse:
    identity = resolve_identity(authorization)

    if audio is None:
        raise AudioMissingError()

    with single_request_per_identity(identity):
        data = await _read_upload(audio)
        if not data:
            raise AudioMissingError()

        return await process_audio_upload(
            data,
            conversation_id=conversation_id,
            language=language or DEFAULT_LANGUAGE,
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
