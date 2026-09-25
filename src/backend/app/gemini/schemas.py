from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.nlp.schemas import AudioIntent, ChatPipelineMetrics, PublicEntity
from app.reports.schemas import WorkflowDirective
from app.alerts.schemas import AlertDirective


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


class SourcePeriod(BaseModel):
    start: str | None = None
    end: str | None = None


class GeminiSource(BaseModel):
    id: str
    title: str
    list_name: str
    web_url: str
    last_modified: str
    score: float
    excerpt: str | None = None
    citation_id: str | None = None
    artifact_id: str | None = None
    extract_id: str | None = None
    project_id: str | None = None
    source_locator: str | None = None
    # Periodo de registro declarado pela fonte, distinto de vigencia.
    registration_period: SourcePeriod | None = None
    validity: SourcePeriod | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class ClaimEvidence(BaseModel):
    citation_id: str
    field: Literal["excerpt", "attribute"]
    attribute: str | None = None
    quote: str = Field(min_length=1)


class FactualClaim(BaseModel):
    text: str
    citation_ids: list[str] = Field(min_length=1)
    evidence: list[ClaimEvidence] = Field(default_factory=list)


class ProactiveSuggestion(BaseModel):
    suggestion_id: str
    intent: str
    description: str
    display_message: str
    requires_confirmation: bool = True


class GeminiChatResponse(BaseModel):
    contract_version: Literal["1.1.0"] = "1.1.0"
    text: str
    model: str
    interaction_id: str | None = None
    trace_id: str | None = None
    latency_ms: int
    retrieval_ms: int = 0
    usage: GeminiUsage
    sources: list[GeminiSource] = Field(default_factory=list)
    claims: list[FactualClaim] = Field(default_factory=list)
    evidence_status: Literal["referenced", "insufficient", "not_applicable"] = "not_applicable"
    trace_sources: list[dict] = Field(default_factory=list, exclude=True)
    intent: AudioIntent | None = None
    entities: list[PublicEntity] = Field(default_factory=list)
    pipeline_metrics: ChatPipelineMetrics = Field(default_factory=ChatPipelineMetrics)
    proactive_suggestion: ProactiveSuggestion | None = None
    workflow: WorkflowDirective | AlertDirective | None = None

    @model_validator(mode="after")
    def validate_claim_references(self):
        ids = [source.citation_id for source in self.sources if source.citation_id]
        if len(ids) != len(set(ids)):
            raise ValueError("Identificador de citacao duplicado")
        if self.evidence_status == "referenced" and not self.claims:
            raise ValueError("Resposta referenciada exige afirmacoes com fontes")
        if self.claims and self.evidence_status != "referenced":
            raise ValueError("Afirmacoes exigem status referenced")
        if any(not set(claim.citation_ids) <= set(ids) for claim in self.claims):
            raise ValueError("Afirmacao referencia fonte inexistente")
        if self.claims:
            from app.gemini.evidence import normalize_quote, source_units

            units = {source.citation_id: source_units(source) for source in self.sources}
            for claim in self.claims:
                if [item.citation_id for item in claim.evidence] != claim.citation_ids:
                    raise ValueError("Cada citacao exige evidencia verificavel")
                if any(item not in units.get(item.citation_id, [])
                       or normalize_quote(claim.text) != normalize_quote(item.quote)
                       for item in claim.evidence):
                    raise ValueError("Afirmacao nao corresponde integralmente a fonte")
            expected = "\n".join(f"{claim.text} " + " ".join(
                f"[{citation_id}]" for citation_id in claim.citation_ids) for claim in self.claims)
            if self.text != expected:
                raise ValueError("Texto deve corresponder as afirmacoes verificadas")
        return self


class ProactiveConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestion_id: str = Field(..., min_length=36, max_length=36)
    conversation_id: str = Field(..., min_length=1, max_length=160)
    decision: Literal["accept", "decline"]


class ProactiveConfirmationResponse(BaseModel):
    status: Literal["accepted", "declined"]
    result: GeminiChatResponse | None = None
