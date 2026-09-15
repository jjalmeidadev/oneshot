"""Troca segura do segredo Direct Line por token curto de uma conversa."""

from __future__ import annotations

import asyncio
import os
from hashlib import sha256
from urllib.parse import urlparse

import httpx

from app.copilot.errors import CopilotConfigurationError, DirectLineUnavailableError
from app.copilot.schemas import DirectLineTokenResponse
from app.copilot.security import CopilotIdentity

DIRECT_LINE_TOKEN_URL = (
    "https://directline.botframework.com/v3/directline/tokens/generate"
)


async def issue_direct_line_token(
    identity: CopilotIdentity,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> DirectLineTokenResponse:
    secret = os.getenv("COPILOT_DIRECT_LINE_SECRET", "").strip()
    if not secret:
        raise CopilotConfigurationError()

    trusted_origins = direct_line_trusted_origins()
    attempts = _bounded_int("COPILOT_DIRECT_LINE_MAX_ATTEMPTS", 2, minimum=1, maximum=3)
    timeout = _bounded_float(
        "COPILOT_DIRECT_LINE_TIMEOUT_SECONDS", 8.0, minimum=1, maximum=30
    )
    body: dict[str, object] = {
        "user": {"id": _direct_line_user_id(identity.object_id)},
    }
    if trusted_origins:
        body["trustedOrigins"] = trusted_origins

    async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
        for attempt in range(attempts):
            try:
                response = await client.post(
                    DIRECT_LINE_TOKEN_URL,
                    headers={"Authorization": f"Bearer {secret}"},
                    json=body,
                )
            except httpx.HTTPError:
                response = None

            if response is not None and response.status_code == 200:
                try:
                    payload = response.json()
                    return DirectLineTokenResponse(
                        token=payload["token"],
                        expires_in=payload["expires_in"],
                        conversation_id=payload["conversationId"],
                    )
                except (KeyError, TypeError, ValueError) as error:
                    raise DirectLineUnavailableError() from error

            retryable = (
                response is None
                or response.status_code == 429
                or response.status_code >= 500
            )
            if not retryable or attempt == attempts - 1:
                break
            await asyncio.sleep(0.2 * (2**attempt))

    raise DirectLineUnavailableError()


def _direct_line_user_id(object_id: str) -> str:
    digest = sha256(object_id.encode("utf-8")).hexdigest()[:32]
    return f"dl_{digest}"


def direct_line_trusted_origins() -> list[str]:
    """Valida origens exatas usadas tanto no CORS quanto no token Direct Line."""

    origins = [
        value.strip().rstrip("/")
        for value in os.getenv("COPILOT_DIRECT_LINE_TRUSTED_ORIGINS", "").split(",")
        if value.strip()
    ]
    for origin in origins:
        parsed = urlparse(origin)
        is_local_http = parsed.scheme == "http" and parsed.hostname in {
            "localhost",
            "127.0.0.1",
        }
        is_origin_only = (
            parsed.path in {"", "/"}
            and not parsed.params
            and not parsed.query
            and not parsed.fragment
            and parsed.username is None
            and parsed.password is None
            and "*" not in (parsed.hostname or "")
        )
        if (
            not parsed.netloc
            or not is_origin_only
            or (parsed.scheme != "https" and not is_local_http)
        ):
            raise CopilotConfigurationError()
    return origins


def _bounded_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as error:
        raise CopilotConfigurationError() from error
    if not minimum <= value <= maximum:
        raise CopilotConfigurationError()
    return value


def _bounded_float(
    name: str, default: float, *, minimum: float, maximum: float
) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError as error:
        raise CopilotConfigurationError() from error
    if not minimum <= value <= maximum:
        raise CopilotConfigurationError()
    return value
