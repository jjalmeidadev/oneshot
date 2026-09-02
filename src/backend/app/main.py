from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.audio.errors import AudioMissingError, AudioValidationError
from app.audio.schemas import AudioUploadResponse
from app.audio.service import process_audio_upload
from app.gemini.client import (
    GeminiAPIError,
    GeminiConfigurationError,
    generate_chat_response,
)
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(
    title="API de IA do Metro",
    description="Chat via Gemini com recuperacao de contexto em listas simuladas do SharePoint.",
    version="0.1.0",
)


@app.exception_handler(AudioValidationError)
def handle_audio_validation_error(
    _request: Request, error: AudioValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "detail": error.detail,
            }
        },
    )


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


@app.post("/api/audio", response_model=AudioUploadResponse)
async def create_audio_upload(
    audio: UploadFile | None = File(default=None),
    conversation_id: str | None = Form(default=None),
    language: str | None = Form(default=None),
) -> AudioUploadResponse:
    if audio is None:
        raise AudioMissingError()

    data = await audio.read()
    if not data:
        raise AudioMissingError()

    # `language` e aceito pelo contrato da Secao 8.7.4 e sera usado quando a
    # integracao real com o Speech-to-Text (task 11) estiver implementada.
    del language

    return process_audio_upload(data, conversation_id=conversation_id)