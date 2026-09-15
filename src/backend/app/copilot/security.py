"""Validacao local de access tokens Microsoft Entra ID para o conector."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Header
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError

from app.copilot.errors import (
    AuthenticationProviderUnavailableError,
    CopilotConfigurationError,
    CopilotForbiddenError,
    CopilotUnauthenticatedError,
)


@dataclass(frozen=True)
class CopilotIdentity:
    object_id: str
    tenant_id: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class EntraSettings:
    tenant_id: str
    audience: str
    issuer: str
    jwks_url: str
    invoke_scope: str
    channel_scope: str
    clock_skew_seconds: int


def require_copilot_invoke(
    authorization: Annotated[str | None, Header()] = None,
) -> CopilotIdentity:
    return authenticate_access_token(
        authorization,
        required_scope=os.getenv(
            "COPILOT_ENTRA_INVOKE_SCOPE", "copilot.invoke"
        ).strip(),
    )


def require_copilot_channel(
    authorization: Annotated[str | None, Header()] = None,
) -> CopilotIdentity:
    return authenticate_access_token(
        authorization,
        required_scope=os.getenv(
            "COPILOT_ENTRA_CHANNEL_SCOPE", "copilot.channel"
        ).strip(),
    )


def authenticate_access_token(
    authorization: str | None,
    *,
    required_scope: str,
    settings: EntraSettings | None = None,
) -> CopilotIdentity:
    scheme, _, token = (authorization or "").partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise CopilotUnauthenticatedError()

    resolved_settings = settings or _settings()
    try:
        signing_key = _jwks_client(resolved_settings.jwks_url).get_signing_key_from_jwt(
            token
        )
        claims: dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=resolved_settings.audience,
            issuer=resolved_settings.issuer,
            leeway=resolved_settings.clock_skew_seconds,
            options={"require": ["aud", "exp", "iat", "iss", "tid"]},
        )
    except PyJWKClientConnectionError as error:
        raise AuthenticationProviderUnavailableError() from error
    except jwt.PyJWTError as error:
        raise CopilotUnauthenticatedError() from error
    except Exception as error:
        # Falha de descoberta/JWKS nao revela URL, chave ou resposta do Entra.
        raise CopilotUnauthenticatedError() from error

    tenant_id = str(claims.get("tid", ""))
    if tenant_id.lower() != resolved_settings.tenant_id.lower():
        raise CopilotUnauthenticatedError()

    object_id = str(claims.get("oid") or claims.get("sub") or "").strip()
    if not object_id:
        raise CopilotUnauthenticatedError()

    scopes = frozenset(str(claims.get("scp", "")).split())
    if required_scope not in scopes:
        raise CopilotForbiddenError()

    return CopilotIdentity(object_id=object_id, tenant_id=tenant_id, scopes=scopes)


@lru_cache(maxsize=1)
def _settings() -> EntraSettings:
    if os.getenv("COPILOT_STUDIO_ENABLED", "0").strip() != "1":
        raise CopilotConfigurationError()

    tenant_id = os.getenv("COPILOT_ENTRA_TENANT_ID", "").strip()
    audience = os.getenv("COPILOT_ENTRA_AUDIENCE", "").strip()
    try:
        UUID(tenant_id)
    except ValueError as error:
        raise CopilotConfigurationError() from error
    if not audience:
        raise CopilotConfigurationError()

    try:
        clock_skew = int(os.getenv("COPILOT_ENTRA_CLOCK_SKEW_SECONDS", "60"))
    except ValueError as error:
        raise CopilotConfigurationError() from error
    if not 0 <= clock_skew <= 300:
        raise CopilotConfigurationError()

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    invoke_scope = os.getenv("COPILOT_ENTRA_INVOKE_SCOPE", "copilot.invoke").strip()
    channel_scope = os.getenv("COPILOT_ENTRA_CHANNEL_SCOPE", "copilot.channel").strip()
    if not invoke_scope or not channel_scope:
        raise CopilotConfigurationError()

    return EntraSettings(
        tenant_id=tenant_id,
        audience=audience,
        issuer=f"{authority}/v2.0",
        jwks_url=f"{authority}/discovery/v2.0/keys",
        invoke_scope=invoke_scope,
        channel_scope=channel_scope,
        clock_skew_seconds=clock_skew,
    )


@lru_cache(maxsize=4)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300)
