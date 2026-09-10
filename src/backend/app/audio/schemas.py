"""Schemas da API de recebimento de audio (Secao 8.7 de docs/Projeto.md)."""

from __future__ import annotations

from pydantic import BaseModel, Field
from app.nlp.schemas import AudioIntent, AudioPipelineMetrics, PublicEntity
from app.gemini.schemas import GeminiChatResponse


class AudioTranscription(BaseModel):
    text: str
    confidence: float
    duration_seconds: float


class AudioAnswerSource(BaseModel):
    artifact: str
    section: str


class AudioAnswer(BaseModel):
    text: str
    sources: list[AudioAnswerSource] = Field(default_factory=list)


class AudioUploadResponse(BaseModel):
    conversation_id: str
    interaction_id: str | None
    transcription: AudioTranscription
    intent: AudioIntent | None
    entities: list[PublicEntity] = Field(default_factory=list)
    answer: AudioAnswer
    chat: GeminiChatResponse | None = None
    pipeline_metrics: AudioPipelineMetrics = Field(default_factory=AudioPipelineMetrics)
    pipeline_status: str = Field(default="completed", description="Transcrição e resposta concluídas pelo pipeline.")


class AudioErrorDetail(BaseModel):
    code: str
    message: str
    # `detail` so aparece quando ha conteudo, como no exemplo da Secao 8.7.6.
    detail: dict[str, object] | None = None


class AudioErrorResponse(BaseModel):
    """Envelope unico de erro, para que o canal exiba a mensagem sem
    interpretar cada caso."""

    error: AudioErrorDetail
