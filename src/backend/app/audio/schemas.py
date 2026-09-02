"""Schemas da API de recebimento de audio (Secao 8.7 de docs/Projeto.md)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AudioTranscription(BaseModel):
    text: str
    confidence: float
    duration_seconds: float


class AudioIntent(BaseModel):
    macro: str
    specific: str
    confidence_macro: float
    confidence_specific: float


class AudioAnswerSource(BaseModel):
    artifact: str
    section: str


class AudioAnswer(BaseModel):
    text: str
    sources: list[AudioAnswerSource] = Field(default_factory=list)


class AudioUploadResponse(BaseModel):
    conversation_id: str
    interaction_id: str
    transcription: AudioTranscription
    intent: AudioIntent
    answer: AudioAnswer
    pipeline_status: str = Field(
        description=(
            "'stubbed' enquanto a integracao real com o Speech-to-Text e o "
            "pipeline de PLN (task 11) nao esta implementada; 'completed' "
            "quando a resposta vem do provedor real."
        ),
    )


class AudioErrorDetail(BaseModel):
    code: str
    message: str
    detail: dict[str, object] = Field(default_factory=dict)


class AudioErrorResponse(BaseModel):
    error: AudioErrorDetail