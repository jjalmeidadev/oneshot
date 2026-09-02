"""Contratos de entrada e saida da API de audio (Secao 8.7 do Projeto.md)."""

from pydantic import BaseModel, Field


class AudioErrorBody(BaseModel):
    code: str
    message: str
    detail: dict | None = None


class AudioErrorResponse(BaseModel):
    """Envelope unico de erro, para que o canal exiba a mensagem sem
    interpretar cada caso."""

    error: AudioErrorBody


class AudioTranscription(BaseModel):
    text: str
    confidence: float | None = None
    duration_seconds: float | None = None


class AudioUploadResponse(BaseModel):
    """Resposta de sucesso do `POST /api/audio`.

    `intent` e `answer` permanecem nulos ate a integracao do pipeline de PLN a
    API, prevista nas issues #126 e #128; a transcricao ja acompanha o formato
    documentado na Secao 8.7.5.
    """

    conversation_id: str
    interaction_id: str
    transcription: AudioTranscription
    intent: dict | None = None
    answer: dict | None = None
