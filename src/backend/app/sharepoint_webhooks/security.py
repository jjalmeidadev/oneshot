"""Validação do segredo compartilhado pelo provedor simulado."""

import hmac
import os

from fastapi import HTTPException, status

from app.sharepoint_webhooks.schemas import SharePointNotificationBatch


def validate_client_state(payload: SharePointNotificationBatch) -> None:
    """Compara todos os valores sem expor o segredo em erros ou logs."""

    expected = os.getenv("SHAREPOINT_WEBHOOK_CLIENT_STATE", "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook do SharePoint simulado não configurado.",
        )

    if any(
        not hmac.compare_digest(
            item.client_state.get_secret_value().encode("utf-8"),
            expected.encode("utf-8"),
        )
        for item in payload.value
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="clientState inválido.",
        )
