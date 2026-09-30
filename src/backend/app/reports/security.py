"""Identidade simulada e autorizacao de escopo para o modo isolado."""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.reports.errors import (
    ReportAccessDeniedError,
    ReportCallbackUnauthorizedError,
    ReportConfigurationError,
)
from app.reports.schemas import ReportScope, ScopeType
from app.security.access import (
    AccessContext,
    AccessOperation,
    PostgresAccessRepository,
    authorize_operation,
)


@dataclass(frozen=True)
class ReportIdentity:
    subject: str
    display_name: str
    role: str
    can_export: bool
    allow_all: bool
    allowed_projects: frozenset[str]
    allowed_subportfolios: frozenset[str]
    can_read: bool = True
    can_write: bool = True
    user_id: str | None = None
    access_context: AccessContext | None = None


def report_identity_from_access_context(context: AccessContext) -> ReportIdentity:
    """Adapta o contexto central aos contratos internos ja existentes."""

    return ReportIdentity(
        subject=str(context.auth_subject),
        display_name=context.role_name,
        role=context.role_name,
        can_export=context.can_export,
        allow_all=any(grant.permission_scope == "portfolio" for grant in context.grants),
        allowed_projects=frozenset(
            {*(str(value) for value in context.allowed_project_ids),
             *context.allowed_project_codes}
        ),
        allowed_subportfolios=frozenset(
            {*(str(value) for value in context.allowed_subportfolio_ids),
             *context.allowed_subportfolio_codes}
        ),
        can_read=context.can_read,
        can_write=context.can_write,
        user_id=str(context.user_id),
        access_context=context,
    )


def resolve_report_identity(authorization: str | None) -> ReportIdentity:
    token = _bearer_token(authorization)
    configured = _configured_identities()
    for expected, payload in configured.items():
        if hmac.compare_digest(token, expected):
            return _identity_from_payload(payload)
    raise ReportAccessDeniedError()


def resolve_report_identity_by_subject(subject: str) -> ReportIdentity:
    """Resolve a identidade persistida para revalidacao em workers sem token."""

    try:
        return report_identity_from_access_context(
            PostgresAccessRepository().resolve(UUID(subject))
        )
    except Exception:
        # Compatibilidade temporaria com jobs e massas antigas da PoC.
        pass

    for payload in _configured_identities().values():
        identity = _identity_from_payload(payload)
        if hmac.compare_digest(identity.subject, subject):
            return identity
    raise ReportAccessDeniedError()


def authorize_scope(
    identity: ReportIdentity,
    scope: ReportScope,
    operation: AccessOperation = "export",
) -> None:
    if identity.access_context is not None:
        authorize_operation(
            identity.access_context,
            operation,
            project_id=scope.id if scope.type == ScopeType.PROJECT else None,
            subportfolio_id=(
                scope.id if scope.type == ScopeType.SUBPORTFOLIO else None
            ),
        )
        return
    if not _has_permission(identity, operation):
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
    identity: ReportIdentity,
    scope_type: ScopeType,
    scope_id: str,
    operation: AccessOperation = "export",
) -> bool:
    if not _has_permission(identity, operation):
        return False
    if identity.allow_all:
        return True
    allowed = (
        identity.allowed_projects
        if scope_type == ScopeType.PROJECT
        else identity.allowed_subportfolios
    )
    return scope_id in allowed


def _has_permission(identity: ReportIdentity, operation: AccessOperation) -> bool:
    return {
        "read": identity.can_read,
        "write": identity.can_write,
        "export": identity.can_export,
    }[operation]


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
            can_read=bool(payload.get("can_read", True)),
            can_write=bool(payload.get("can_write", payload.get("can_export", False))),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ReportConfigurationError() from error


def validate_callback_token(value: str | None) -> None:
    expected = os.getenv("REPORT_CALLBACK_TOKEN", "").strip()
    if not expected:
        raise ReportConfigurationError()
    if value is None or not hmac.compare_digest(value, expected):
        raise ReportCallbackUnauthorizedError()
