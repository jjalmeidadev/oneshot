from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.nlp.schemas import AudioIntent, ChatPipelineMetrics, PublicEntity


class GeminiChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=20000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=160)
    previous_interaction_id: str | None = Field(default=None, max_length=1024)
    use_intent_classifier: bool = True
    proactivity_enabled: bool = False

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Mensagem vazia")
        return value


class GeminiUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    thought_tokens: int = 0
    total_tokens: int = 0


class GeminiSource(BaseModel):
    id: str
    title: str
    list_name: str
    web_url: str
    last_modified: str
    score: float
    excerpt: str | None = None


class ProactiveSuggestion(BaseModel):
    suggestion_id: str
    intent: str
    description: str
    display_message: str
    requires_confirmation: bool = True


class GeminiChatResponse(BaseModel):
    text: str
    model: str
    interaction_id: str | None = None
    latency_ms: int
    retrieval_ms: int = 0
    usage: GeminiUsage
    sources: list[GeminiSource] = Field(default_factory=list)
    trace_sources: list[dict] = Field(default_factory=list, exclude=True)
    intent: AudioIntent | None = None
    entities: list[PublicEntity] = Field(default_factory=list)
    pipeline_metrics: ChatPipelineMetrics = Field(default_factory=ChatPipelineMetrics)
    proactive_suggestion: ProactiveSuggestion | None = None


class ProactiveConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestion_id: str = Field(..., min_length=36, max_length=36)
    conversation_id: str = Field(..., min_length=1, max_length=160)
    decision: Literal["accept", "decline"]


class ProactiveConfirmationResponse(BaseModel):
    status: Literal["accepted", "declined"]
    result: GeminiChatResponse | None = None
