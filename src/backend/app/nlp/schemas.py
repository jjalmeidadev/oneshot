"""Resultado público da classificação, compartilhado por texto e áudio."""
from pydantic import BaseModel, Field


class IntentAlternative(BaseModel):
    intent: str
    confidence: float


class AudioIntent(BaseModel):
    macro: str
    specific: str
    confidence_macro: float
    confidence_specific: float
    flow: str = ""
    handler: str = ""
    alternatives: list[IntentAlternative] = Field(default_factory=list)
    routing_rule: str | None = None


class PublicEntity(BaseModel):
    type: str
    value: str
    text: str
    start: int
    end: int
    types: list[str] = Field(default_factory=list)
    ambiguous: bool = False


class ChatPipelineMetrics(BaseModel):
    nlp_ms: int = 0
    route_ms: int = 0


class AudioPipelineMetrics(ChatPipelineMetrics):
    validation_ms: int = 0
    stt_ms: int = 0
    total_ms: int = 0
