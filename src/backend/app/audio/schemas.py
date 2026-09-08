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
            "'stubbed' enquanto o pipeline de PLN nao esta implementado; "
            "'completed' quando a classificacao e a resposta fundamentada "
            "forem geradas pela API."
        ),
    )


class AudioErrorDetail(BaseModel):
    code: str
    message: str
    # `detail` so aparece quando ha conteudo, como no exemplo da Secao 8.7.6.
    detail: dict[str, object] | None = None


class AudioErrorResponse(BaseModel):
    """Envelope unico de erro, para que o canal exiba a mensagem sem
    interpretar cada caso."""

    error: AudioErrorDetail
