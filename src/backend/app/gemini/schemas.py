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


class GeminiChatResponse(BaseModel):
    text: str
    model: str
    interaction_id: str | None = None
    latency_ms: int
    retrieval_ms: int = 0
    usage: GeminiUsage
    sources: list[GeminiSource] = Field(default_factory=list)
