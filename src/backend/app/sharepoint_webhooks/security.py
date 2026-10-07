"""Validação do segredo compartilhado pelo provedor simulado."""

import hmac
import os

from app.sharepoint_webhooks.schemas import SharePointNotificationBatch


class SharePointWebhookNotConfiguredError(RuntimeError):
    """O segredo do provedor simulado não foi configurado."""


class SharePointWebhookUnauthorizedError(RuntimeError):
    """O clientState recebido não corresponde ao segredo esperado."""


def validate_client_state(payload: SharePointNotificationBatch) -> None:
    """Compara todos os valores sem expor o segredo em erros ou logs."""

    expected = os.getenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", "").strip()
    if not expected:
        raise SharePointWebhookNotConfiguredError()

    if any(
        not hmac.compare_digest(
            item.client_state.get_secret_value().encode("utf-8"),
            expected.encode("utf-8"),
        )
        for item in payload.value
    ):
        raise SharePointWebhookUnauthorizedError()
