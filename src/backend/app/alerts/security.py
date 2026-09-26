"""Autenticacao dos callbacks externos de notificacao."""

import hmac
import os

from app.alerts.errors import (
    AlertConfigurationError,
    NotificationCallbackUnauthorizedError,
)


def validate_notification_callback_token(value: str | None) -> None:
    expected = os.getenv("NOTIFICATION_CALLBACK_TOKEN", "").strip()
    if not expected:
        raise AlertConfigurationError("NOTIFICATION_CALLBACK_TOKEN ausente.")
    if not hmac.compare_digest(value or "", expected):
        raise NotificationCallbackUnauthorizedError()
