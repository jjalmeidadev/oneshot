"""Dependencias HTTP compartilhadas para autenticacao e autorizacao."""

from typing import Annotated
from uuid import uuid4

from fastapi import Depends, Header, Request

from app.security.access import (
    AccessContext,
    AccessOperation,
    OutOfScopeForProfileError,
    audit_authorization_denial,
    authorize_operation,
    resolve_access_context,
)


def get_access_context(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AccessContext:
    context = resolve_access_context(authorization)
    request.state.access_context = context
    request.state.access_correlation_id = str(uuid4())
    return context


def _require_operation(
    request: Request,
    context: AccessContext,
    operation: AccessOperation,
) -> AccessContext:
    request.state.access_context = context
    correlation_id = getattr(request.state, "access_correlation_id", None)
    if correlation_id is None:
        correlation_id = str(uuid4())
        request.state.access_correlation_id = correlation_id
    request.state.access_operation = operation
    authorize_operation(
        context,
        operation,
        correlation_id=correlation_id,
    )
    return context


def require_read_access(
    request: Request,
    context: Annotated[AccessContext, Depends(get_access_context)],
) -> AccessContext:
    return _require_operation(request, context, "read")


def require_write_access(
    request: Request,
    context: Annotated[AccessContext, Depends(get_access_context)],
) -> AccessContext:
    return _require_operation(request, context, "write")


def require_export_access(
    request: Request,
    context: Annotated[AccessContext, Depends(get_access_context)],
) -> AccessContext:
    return _require_operation(request, context, "export")


def audit_request_denial(
    request: Request,
    denial: OutOfScopeForProfileError | None = None,
) -> None:
    context = getattr(request.state, "access_context", None)
    if context is None:
        return
    if denial is None:
        denial = OutOfScopeForProfileError(
            getattr(request.state, "access_operation", "read"),
            correlation_id=getattr(request.state, "access_correlation_id", None),
        )
    audit_authorization_denial(context, denial)
