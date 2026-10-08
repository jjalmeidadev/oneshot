"""Publicação assíncrona dos eventos persistidos pela S5-09."""

from __future__ import annotations

from app.alerts.messaging import Message, RabbitMQBroker, SHAREPOINT_ROUTING_KEY
from app.sharepoint_webhooks.repository import (
    SharePointWebhookRepository,
    get_sharepoint_webhook_repository,
)


async def publish_pending_sharepoint_once(
    *,
    repository: SharePointWebhookRepository | None = None,
    broker: RabbitMQBroker | None = None,
    limit: int = 100,
) -> int:
    """Publica um lote; falhas permanecem pendentes para nova tentativa."""

    selected_repository = repository or get_sharepoint_webhook_repository()
    selected_broker = broker or RabbitMQBroker()
    owns_broker = broker is None
    published = 0
    try:
        for event in selected_repository.list_pending(limit):
            try:
                await selected_broker.publish(
                    Message(
                        event_id=event.event_id,
                        event_type=SHAREPOINT_ROUTING_KEY,
                        correlation_id=str(
                            event.payload.get("subscriptionId") or event.event_id
                        ),
                        payload=event.payload,
                    )
                )
            except Exception:
                continue
            if selected_repository.mark_published(event.event_id):
                published += 1
    finally:
        if owns_broker:
            await selected_broker.close()
    return published
