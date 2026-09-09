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
    flow: str = ""
    handler: str = ""
    alternatives: list[dict[str, float | str]] = Field(default_factory=list)


class AudioEntity(BaseModel):
    type: str
    value: str
    text: str
    start: int
    end: int
    types: list[str] = Field(default_factory=list)
    ambiguous: bool = False


class AudioPipelineMetrics(BaseModel):
    validation_ms: int = 0
    stt_ms: int = 0
    nlp_ms: int = 0
    total_ms: int = 0


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
    entities: list[AudioEntity] = Field(default_factory=list)
    answer: AudioAnswer
    pipeline_status: str = Field(
        description=(
            "'completed' quando STT e PLN concluem o processamento da "
            "solicitacao de audio."
        ),
    )
    pipeline_metrics: AudioPipelineMetrics = Field(
        default_factory=AudioPipelineMetrics
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
