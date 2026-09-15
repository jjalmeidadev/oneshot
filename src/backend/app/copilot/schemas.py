"""Contratos publicos da fronteira Copilot Studio/backend."""

from __future__ import annotations

from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from app.nlp.schemas import AudioIntent, PublicEntity


class CopilotDispatchRequest(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    conversation_id: str = Field(..., min_length=1, max_length=160)
    message: str = Field(..., min_length=1, max_length=20_000)
    model_route: str = Field(default="auto", min_length=1, max_length=32)

    @field_validator("conversation_id", "message", "model_route")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campo obrigatorio vazio")
        return value

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id(cls, value: str) -> str:
        if any(character in value for character in "\r\n\t"):
            raise ValueError("Identificador de conversa invalido")
        return value


class CopilotDispatchResponse(BaseModel):
    correlation_id: str
    request_id: UUID
    execution_id: UUID
    interaction_id: str | None = None
    status: Literal["accepted", "blocked"]
    route_taken: Literal["copilot_topic", "sharepoint_query", "fora_escopo"]
    model_route: Literal["auto", "gpt", "claude"]
    intent: AudioIntent
    entities: list[PublicEntity] = Field(default_factory=list)


class DirectLineTokenResponse(BaseModel):
    token: str = Field(..., min_length=1)
    expires_in: int = Field(..., gt=0)
    conversation_id: str = Field(..., min_length=1)
