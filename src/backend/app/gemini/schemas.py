from pydantic import BaseModel, Field


class GeminiChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=20000)
    previous_interaction_id: str | None = Field(default=None, max_length=1024)


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


class ChatIntentAlternative(BaseModel):
    intent: str
    confidence: float


class ChatIntent(BaseModel):
    macro: str
    specific: str | None = None
    confidence_macro: float
    confidence_specific: float
    flow: str
    handler: str
    alternatives: list[ChatIntentAlternative] = Field(default_factory=list)


class ChatEntity(BaseModel):
    type: str
    value: str
    text: str
    start: int
    end: int
    types: list[str] = Field(default_factory=list)
    ambiguous: bool = False


class ChatPipelineMetrics(BaseModel):
    nlp_ms: int
    route_ms: int


class GeminiChatResponse(BaseModel):
    text: str
    model: str
    interaction_id: str | None = None
    latency_ms: int
    retrieval_ms: int = 0
    usage: GeminiUsage
    sources: list[GeminiSource] = Field(default_factory=list)
    intent: ChatIntent = Field(
        default_factory=lambda: ChatIntent(
            macro="INDEFINIDA",
            specific=None,
            confidence_macro=0.0,
            confidence_specific=0.0,
            flow="nao_classificado",
            handler="nao_classificado",
        )
    )
    entities: list[ChatEntity] = Field(default_factory=list)
    pipeline_metrics: ChatPipelineMetrics = Field(
        default_factory=lambda: ChatPipelineMetrics(nlp_ms=0, route_ms=0)
    )
