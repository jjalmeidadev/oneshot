"""Schemas da API de recebimento de audio (Secao 8.7 de docs/Projeto.md)."""

from __future__ import annotations

from pydantic import BaseModel, Field
from app.nlp.schemas import AudioIntent, AudioPipelineMetrics, PublicEntity
from app.gemini.schemas import GeminiChatResponse, GeminiSource, FactualClaim
from typing import Literal

MAX_CONVERSATION_ID_LENGTH = 160


class AudioTranscription(BaseModel):
    text: str
    confidence: float
    duration_seconds: float


class AudioAnswerSource(GeminiSource):
    artifact: str
    section: str


class AudioAnswer(BaseModel):
    text: str
    sources: list[AudioAnswerSource] = Field(default_factory=list)
    claims: list[FactualClaim] = Field(default_factory=list)
    evidence_status: Literal["referenced", "insufficient", "not_applicable"] = "not_applicable"


class AudioUploadResponse(BaseModel):
    contract_version: Literal["1.1.0"] = "1.1.0"
    conversation_id: str = Field(max_length=MAX_CONVERSATION_ID_LENGTH)
    interaction_id: str | None
    trace_id: str | None = None
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
