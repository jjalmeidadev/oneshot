"""Identidade simulada e autorizacao de escopo para o modo isolado."""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass
from typing import Any

from app.reports.errors import ReportAccessDeniedError, ReportConfigurationError
from app.reports.schemas import ReportScope, ScopeType


@dataclass(frozen=True)
class ReportIdentity:
    subject: str
    display_name: str
    role: str
    can_export: bool
    allow_all: bool
    allowed_projects: frozenset[str]
    allowed_subportfolios: frozenset[str]


def resolve_report_identity(authorization: str | None) -> ReportIdentity:
    token = _bearer_token(authorization)
    configured = _configured_identities()
    for expected, payload in configured.items():
        if hmac.compare_digest(token, expected):
            return _identity_from_payload(payload)
    raise ReportAccessDeniedError()


def resolve_report_identity_by_subject(subject: str) -> ReportIdentity:
    """Resolve a identidade persistida para revalidacao em workers sem token."""

    for payload in _configured_identities().values():
        identity = _identity_from_payload(payload)
        if hmac.compare_digest(identity.subject, subject):
            return identity
    raise ReportAccessDeniedError()


def authorize_scope(identity: ReportIdentity, scope: ReportScope) -> None:
    if not identity.can_export:
        raise ReportAccessDeniedError()
    if identity.allow_all:
        return
    allowed = (
        identity.allowed_projects
        if scope.type == ScopeType.PROJECT
        else identity.allowed_subportfolios
    )
    if scope.id not in allowed:
        raise ReportAccessDeniedError()


def can_access_scope(
    identity: ReportIdentity, scope_type: ScopeType, scope_id: str
) -> bool:
    if not identity.can_export:
        return False
    if identity.allow_all:
        return True
    allowed = (
        identity.allowed_projects
        if scope_type == ScopeType.PROJECT
        else identity.allowed_subportfolios
    )
    return scope_id in allowed


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise ReportAccessDeniedError()
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise ReportAccessDeniedError()
    return token


def _configured_identities() -> dict[str, dict[str, Any]]:
    raw = os.getenv("REPORT_SIMULATED_IDENTITIES", "").strip()
    if not raw:
        raise ReportConfigurationError()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ReportConfigurationError() from error
    if not isinstance(value, dict) or not value:
        raise ReportConfigurationError()
    return value


def _identity_from_payload(payload: dict[str, Any]) -> ReportIdentity:
    try:
        return ReportIdentity(
            subject=str(payload["subject"]),
            display_name=str(payload.get("display_name") or payload["subject"]),
            role=str(payload["role"]),
            can_export=bool(payload.get("can_export", False)),
            allow_all=bool(payload.get("allow_all", False)),
            allowed_projects=frozenset(map(str, payload.get("projects", []))),
            allowed_subportfolios=frozenset(map(str, payload.get("subportfolios", []))),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ReportConfigurationError() from error


def validate_callback_token(value: str | None) -> None:
    expected = os.getenv("REPORT_CALLBACK_TOKEN", "").strip()
    if not expected:
        raise ReportConfigurationError()
    if value is None or not hmac.compare_digest(value, expected):
        raise ReportAccessDeniedError()
