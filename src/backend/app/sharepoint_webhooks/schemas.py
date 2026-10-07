"""Contrato HTTP das notificações do SharePoint simulado."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


class StrictWebhookModel(BaseModel):
    """Rejeita extensões silenciosas no contrato do provedor simulado."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SharePointChangeType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class SharePointResourceData(StrictWebhookModel):
    site_id: str = Field(alias="siteId", min_length=1, max_length=160)
    list_id: str = Field(
        alias="listId",
        min_length=1,
        max_length=160,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )
    item_id: int = Field(alias="itemId", ge=1)
    partner_source_id: str = Field(
        alias="partnerSourceId", min_length=1, max_length=240
    )

    @model_validator(mode="after")
    def validate_partner_source_id(self) -> "SharePointResourceData":
        expected = f"sharepoint-mock:{self.list_id}:{self.item_id}"
        if self.partner_source_id != expected:
            raise ValueError("partnerSourceId não corresponde à lista e ao item")
        return self


class SharePointChangeNotification(StrictWebhookModel):
    event_id: UUID = Field(alias="eventId")
    subscription_id: str = Field(
        alias="subscriptionId", min_length=1, max_length=160
    )
    client_state: SecretStr = Field(alias="clientState")
    change_type: SharePointChangeType = Field(alias="changeType")
    resource: str = Field(min_length=1, max_length=320)
    resource_data: SharePointResourceData = Field(alias="resourceData")
    occurred_at: datetime = Field(alias="occurredAt")

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurredAt deve informar fuso horário")
        return value

    @model_validator(mode="after")
    def validate_resource_locator(self) -> "SharePointChangeNotification":
        expected = (
            f"lists/{self.resource_data.list_id}/items/"
            f"{self.resource_data.item_id}"
        )
        if self.resource != expected:
            raise ValueError("resource não corresponde à lista e ao item")
        return self


class SharePointNotificationBatch(StrictWebhookModel):
    value: list[SharePointChangeNotification] = Field(min_length=1, max_length=100)


class SharePointWebhookResponse(StrictWebhookModel):
    status: Literal["accepted"] = "accepted"
    accepted: int = Field(ge=1, le=100)
    created: int = Field(ge=0, le=100)
    duplicates: int = Field(ge=0, le=100)


class SharePointPublishedNotification(StrictWebhookModel):
    """Payload sanitizado publicado na fila, sem o segredo clientState."""

    event_id: UUID = Field(alias="eventId")
    subscription_id: str = Field(
        alias="subscriptionId", min_length=1, max_length=160
    )
    change_type: SharePointChangeType = Field(alias="changeType")
    resource: str = Field(min_length=1, max_length=320)
    resource_data: SharePointResourceData = Field(alias="resourceData")
    occurred_at: datetime = Field(alias="occurredAt")

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurredAt deve informar fuso horário")
        return value

    @model_validator(mode="after")
    def validate_resource_locator(self) -> "SharePointPublishedNotification":
        expected = (
            f"lists/{self.resource_data.list_id}/items/"
            f"{self.resource_data.item_id}"
        )
        if self.resource != expected:
            raise ValueError("resource não corresponde à lista e ao item")
        return self


class SharePointChangeEvent(StrictWebhookModel):
    event_id: UUID
    event_type: Literal["sharepoint.change.received"]
    correlation_id: str = Field(min_length=1, max_length=160)
    payload: SharePointPublishedNotification

    @model_validator(mode="after")
    def validate_event_id(self) -> "SharePointChangeEvent":
        if self.event_id != self.payload.event_id:
            raise ValueError("event_id do envelope difere do payload")
        return self
