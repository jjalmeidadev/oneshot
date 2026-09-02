from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.audio import errors as audio_errors
from app.audio.router import router as audio_router
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    generate_chat_response,
)
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

AUDIO_PATH = "/api/audio"

app = FastAPI(
    title="API de IA do Metro",
    description="Chat via Gemini com recuperacao de contexto em listas simuladas do SharePoint.",
    version="0.1.0",
)

app.include_router(audio_router)


@app.exception_handler(audio_errors.AudioError)
async def handle_audio_error(
    _request: Request, error: audio_errors.AudioError
) -> JSONResponse:
    """Converte os cenarios previstos no envelope unico da Secao 8.7.6."""

    return JSONResponse(status_code=error.status_code, content=error.to_payload())


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request, error: RequestValidationError
):
    """Impede que o detalhamento de validacao do FastAPI chegue ao usuario.

    O corpo padrao expoe caminho de campo e tipo interno esperado, o que o RNF11
    nao admite na resposta ao usuario final. Na rota de audio a falha e
    reescrita como `AUDIO_MISSING`, unico caso possivel de corpo invalido no
    contrato multipart; as demais rotas mantem o comportamento padrao.
    """

    if request.url.path != AUDIO_PATH:
        return await request_validation_exception_handler(request, error)

    missing = audio_errors.audio_missing()
    return JSONResponse(status_code=missing.status_code, content=missing.to_payload())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=GeminiChatResponse)
def create_chat_response(request: GeminiChatRequest) -> GeminiChatResponse:
    try:
        return generate_chat_response(request)
    except GeminiConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except GeminiAPIError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
