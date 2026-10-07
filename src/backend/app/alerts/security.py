"""Autenticacao dos callbacks externos de notificacao."""

import hashlib
import hmac
import os
import re

from app.alerts.errors import (
    AlertConfigurationError,
    NotificationCallbackUnauthorizedError,
)


_SIGNATURE_PATTERN = re.compile(r"sha256=([0-9a-fA-F]{64})")


def validate_notification_callback_signature(
    body: bytes, value: str | None
) -> None:
    secret = os.getenv("NOTIFICATION_CALLBACK_SECRET", "").strip()
    if not secret:
        raise AlertConfigurationError("NOTIFICATION_CALLBACK_SECRET ausente.")

    match = _SIGNATURE_PATTERN.fullmatch((value or "").strip())
    if match is None:
        raise NotificationCallbackUnauthorizedError()

    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(match.group(1).lower(), expected):
        raise NotificationCallbackUnauthorizedError()
