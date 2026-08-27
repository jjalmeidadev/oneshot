from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response

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
