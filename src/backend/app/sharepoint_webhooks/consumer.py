"""Consumer idempotente das alterações do SharePoint simulado."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from app.alerts.messaging import Message, RabbitMQBroker, SHAREPOINT_ROUTING_KEY
from app.rag.reindex import reindex_sharepoint_mock
from app.sharepoint_webhooks.repository import (
    SharePointWebhookRepository,
    get_sharepoint_webhook_repository,
    hash_payload,
)
from app.sharepoint_webhooks.schemas import SharePointChangeEvent


class SharePointWebhookMessageError(RuntimeError):
    """Envelope AMQP inválido ou divergente da inbox."""


def _reindex_source(_partner_source_id: str) -> object:
    """Reaplica a massa inteira; a operação S5-12 ainda é global."""

    return reindex_sharepoint_mock()


def process_sharepoint_change_message(
    message: Message,
    *,
    repository: SharePointWebhookRepository | None = None,
    reindex_source: Callable[[str], Any] | None = None,
) -> bool:
    try:
        event = SharePointChangeEvent.model_validate(message.__dict__)
    except ValidationError as error:
        raise SharePointWebhookMessageError("Envelope SharePoint inválido.") from error

    selected_repository = repository or get_sharepoint_webhook_repository()
    event_id = str(event.event_id)
    stored = selected_repository.get_payload(event_id)
    if stored is None or hash_payload(stored) != hash_payload(message.payload):
        raise SharePointWebhookMessageError(
            "Evento SharePoint ausente ou divergente da inbox."
        )
    if not selected_repository.claim_for_processing(event_id):
        return False

    operation = reindex_source or _reindex_source
    try:
        operation(event.payload.resource_data.partner_source_id)
    except Exception:
        selected_repository.mark_processing_failed(
            event_id,
            "SHAREPOINT_REINDEX_FAILED",
        )
        raise
    if not selected_repository.mark_processed(event_id):
        raise SharePointWebhookMessageError(
            "Não foi possível concluir o evento SharePoint."
        )
    return True


async def run_sharepoint_consumer() -> None:
    broker = RabbitMQBroker()

    async def handle(message: Message) -> None:
        process_sharepoint_change_message(message)

    try:
        await broker.consume(SHAREPOINT_ROUTING_KEY, handle)
    finally:
        await broker.close()
