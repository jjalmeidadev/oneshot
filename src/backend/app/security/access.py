"""Validacao Supabase Auth e resolucao das regras de acesso da aplicacao.

O token e confirmado por uma chamada server-side ao Supabase Auth. Somente o
``sub`` validado cruza a fronteira para o banco; papel, escopo e permissoes
vindos do cliente ou de ``user_metadata`` nunca participam da autorizacao.
"""

from __future__ import annotations

import base64
import binascii
from collections.abc import Callable
from dataclasses import dataclass
import json
import logging
import os
import re
from typing import Any, Literal, Protocol
from uuid import UUID, uuid4

import httpx
from pydantic import BaseModel, Field

from app.database.connection import open_database_connection


AUTH_TIMEOUT_SECONDS = 10
PUBLIC_KEY_ENV_NAMES = ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY")
PROJECT_REFERENCE_PATTERN = re.compile(
    r"\b(?:PRJ-[A-Z0-9-]+|S5-03-DEMO-PROJECT)\b",
    re.IGNORECASE,
)
AccessOperation = Literal["read", "write", "export"]
ProfileKey = Literal[
    "pmo",
    "lider_subportfolio",
    "gerente_projeto",
    "consulta",
]
PROFILE_KEYS = {
    "pmo": "pmo",
    "lider_subportfolio": "lider_subportfolio",
    "equipe_projeto": "gerente_projeto",
    "consulta": "consulta",
}
PERSONA_EMAILS: dict[ProfileKey, str] = {
    "pmo": "mvp.pmo@oneshot.example.com",
    "lider_subportfolio": "mvp.lider-subportfolio@oneshot.example.com",
    "gerente_projeto": "mvp.gerente-projeto@oneshot.example.com",
    "consulta": "mvp.consulta@oneshot.example.com",
}
logger = logging.getLogger(__name__)


class AccessError(Exception):
    """Erro esperado de autenticacao ou configuracao do perfil de acesso."""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

    def to_payload(self) -> dict[str, dict[str, str]]:
        return {"error": {"code": self.code, "message": self.message}}


class AuthenticationRequiredError(AccessError):
    def __init__(self) -> None:
        super().__init__(
            "AUTHENTICATION_REQUIRED",
            "Informe um token de acesso Bearer.",
            401,
        )


class InvalidAccessTokenError(AccessError):
    def __init__(self) -> None:
        super().__init__(
            "INVALID_ACCESS_TOKEN",
            "O token de acesso e invalido ou expirou.",
            401,
        )


class InvalidCredentialsError(AccessError):
    def __init__(self) -> None:
        super().__init__(
            "INVALID_CREDENTIALS",
            "Persona ou senha inválida.",
            401,
        )


class AuthenticationUnavailableError(AccessError):
    def __init__(self) -> None:
        super().__init__(
            "AUTHENTICATION_UNAVAILABLE",
            "O serviço de autenticação está indisponível. Tente novamente.",
            503,
        )


class AccessProfileNotConfiguredError(AccessError):
    def __init__(self) -> None:
        super().__init__(
            "ACCESS_PROFILE_NOT_CONFIGURED",
            "O usuario autenticado nao possui perfil de acesso configurado.",
            403,
        )


class UserInactiveError(AccessError):
    def __init__(self) -> None:
        super().__init__(
            "USER_INACTIVE",
            "O usuario autenticado esta inativo.",
            403,
        )


class OutOfScopeForProfileError(AccessError):
    def __init__(
        self,
        operation: AccessOperation,
        *,
        project_id: str | None = None,
        subportfolio_id: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            "OUT_OF_SCOPE_FOR_PROFILE",
            "A operacao solicitada nao esta disponivel para este perfil.",
            403,
        )
        self.operation = operation
        self.project_id = project_id
        self.subportfolio_id = subportfolio_id
        self.correlation_id = correlation_id or str(uuid4())


@dataclass(frozen=True)
class AuthIdentity:
    """Identidade confirmada pelo servidor do Supabase Auth."""

    subject: UUID


@dataclass(frozen=True)
class AccessGrant:
    """Regra ativa preservada para futuras checagens por alvo e operacao."""

    permission_scope: str
    subportfolio_id: UUID | None
    project_id: UUID | None
    can_read: bool
    can_write: bool
    can_export: bool
    subportfolio_code: str | None = None
    project_code: str | None = None


@dataclass(frozen=True)
class AccessContext:
    """Contexto confiavel derivado de Auth validado e do banco da aplicacao."""

    user_id: UUID
    auth_subject: UUID
    role_name: str
    allowed_subportfolio_ids: frozenset[UUID]
    allowed_project_ids: frozenset[UUID]
    can_read: bool
    can_write: bool
    can_export: bool
    grants: tuple[AccessGrant, ...]
    allowed_subportfolio_codes: frozenset[str] = frozenset()
    allowed_project_codes: frozenset[str] = frozenset()
    display_name: str = ""
    email: str = ""


class AccessProfileResponse(BaseModel):
    """Contrato minimo e seguro consumido pela tela de entrada."""

    display_name: str
    email: str
    role_name: str
    profile_key: str
    scope_label: str
    can_read: bool
    can_write: bool
    can_export: bool


class PasswordLoginRequest(BaseModel):
    """Credenciais mínimas aceitas pela entrada simplificada do MVP."""

    profile_key: ProfileKey
    password: str = Field(min_length=1, max_length=256)


class PasswordLoginResponse(BaseModel):
    """JWT temporário e perfil verificado devolvidos após o login."""

    access_token: str
    profile: AccessProfileResponse


class TokenVerifier(Protocol):
    def verify(self, access_token: str) -> AuthIdentity: ...


class AccessRepository(Protocol):
    def resolve(self, auth_subject: UUID) -> AccessContext: ...


class SupabaseAuthVerifier:
    """Valida o access token pela API Auth sem usar a service role."""

    def __init__(
        self,
        supabase_url: str | None = None,
        public_key: str | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "")).strip()
        self._public_key = public_key or _public_api_key()
        self._client = client
        if not self._supabase_url:
            raise RuntimeError("Configure SUPABASE_URL no ambiente do backend.")
        if not self._public_key:
            raise RuntimeError(
                "Configure SUPABASE_PUBLISHABLE_KEY ou SUPABASE_ANON_KEY no backend."
            )
        if _is_privileged_key(self._public_key):
            raise RuntimeError("Use uma chave publicavel, nunca uma secret/service role.")

    def verify(self, access_token: str) -> AuthIdentity:
        owned_client = self._client is None
        client = self._client or httpx.Client(timeout=AUTH_TIMEOUT_SECONDS)
        try:
            response = client.get(
                self._supabase_url.rstrip("/") + "/auth/v1/user",
                headers={
                    "apikey": self._public_key,
                    "Authorization": f"Bearer {access_token}",
                },
            )
        except httpx.HTTPError as error:
            raise InvalidAccessTokenError() from error
        finally:
            if owned_client:
                client.close()

        if response.status_code != 200:
            raise InvalidAccessTokenError()
        try:
            subject = UUID(str(response.json()["id"]))
        except (KeyError, TypeError, ValueError) as error:
            raise InvalidAccessTokenError() from error
        return AuthIdentity(subject=subject)


class SupabasePasswordAuthenticator:
    """Troca e-mail sintético e senha por um JWT no Supabase Auth."""

    def __init__(
        self,
        supabase_url: str | None = None,
        public_key: str | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "")).strip()
        self._public_key = public_key or _public_api_key()
        self._client = client
        if not self._supabase_url:
            raise RuntimeError("Configure SUPABASE_URL no ambiente do backend.")
        if not self._public_key:
            raise RuntimeError(
                "Configure SUPABASE_PUBLISHABLE_KEY ou SUPABASE_ANON_KEY no backend."
            )
        if _is_privileged_key(self._public_key):
            raise RuntimeError("Use uma chave publicavel, nunca uma secret/service role.")

    def sign_in(self, email: str, password: str) -> str:
        owned_client = self._client is None
        client = self._client or httpx.Client(timeout=AUTH_TIMEOUT_SECONDS)
        try:
            response = client.post(
                self._supabase_url.rstrip("/") + "/auth/v1/token",
                params={"grant_type": "password"},
                headers={
                    "apikey": self._public_key,
                    "Content-Type": "application/json",
                },
                json={"email": email, "password": password},
            )
        except httpx.HTTPError as error:
            raise AuthenticationUnavailableError() from error
        finally:
            if owned_client:
                client.close()

        if response.status_code in {400, 401}:
            raise InvalidCredentialsError()
        if response.status_code != 200:
            raise AuthenticationUnavailableError()
        try:
            access_token = str(response.json()["access_token"]).strip()
        except (KeyError, TypeError, ValueError) as error:
            raise AuthenticationUnavailableError() from error
        if not access_token:
            raise AuthenticationUnavailableError()
        return access_token


class PostgresAccessRepository:
    """Resolve o perfil e expande escopos hierarquicos no PostgreSQL."""

    def __init__(
        self,
        open_connection: Callable[[], Any] = open_database_connection,
    ) -> None:
        self._open_connection = open_connection

    def resolve(self, auth_subject: UUID) -> AccessContext:
        connection = self._open_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, display_name, email, role_name, is_active
                      FROM public.users
                     WHERE entra_object_id = %s
                    """,
                    (str(auth_subject),),
                )
                user = cursor.fetchone()
                if user is None:
                    raise AccessProfileNotConfiguredError()
                user_id, display_name, email, role_name, is_active = user
                if not is_active:
                    raise UserInactiveError()

                cursor.execute(
                    """
                    SELECT ar.permission_scope, ar.subportfolio_id, ar.project_id,
                           ar.can_read, ar.can_write, ar.can_export,
                           sp.code, p.code
                      FROM public.access_rules ar
                 LEFT JOIN public.subportfolios sp ON sp.id = ar.subportfolio_id
                 LEFT JOIN public.projects p ON p.id = ar.project_id
                     WHERE ar.user_id = %s AND ar.is_active = TRUE
                     ORDER BY ar.permission_scope, ar.subportfolio_id, ar.project_id
                    """,
                    (user_id,),
                )
                rule_rows = cursor.fetchall()
                if not rule_rows:
                    raise AccessProfileNotConfiguredError()

                grants = tuple(_grant_from_row(row) for row in rule_rows)
                allowed_subportfolios = {
                    grant.subportfolio_id
                    for grant in grants
                    if grant.subportfolio_id is not None
                }
                allowed_projects = {
                    grant.project_id
                    for grant in grants
                    if grant.project_id is not None
                }
                allowed_subportfolio_codes = {
                    grant.subportfolio_code.casefold()
                    for grant in grants
                    if grant.subportfolio_code
                }
                allowed_project_codes = {
                    grant.project_code.casefold()
                    for grant in grants
                    if grant.project_code
                }
                portfolio_access = any(
                    grant.permission_scope == "portfolio" for grant in grants
                )

                if portfolio_access:
                    cursor.execute(
                        "SELECT id, code FROM public.subportfolios WHERE is_active = TRUE"
                    )
                    for row in cursor.fetchall():
                        allowed_subportfolios.add(row[0])
                        if len(row) > 1 and row[1]:
                            allowed_subportfolio_codes.add(str(row[1]).casefold())
                    cursor.execute(
                        """
                        SELECT p.id, p.code
                          FROM public.projects p
                          JOIN public.subportfolios sp ON sp.id = p.subportfolio_id
                         WHERE sp.is_active = TRUE
                        """
                    )
                    for row in cursor.fetchall():
                        allowed_projects.add(row[0])
                        if len(row) > 1 and row[1]:
                            allowed_project_codes.add(str(row[1]).casefold())
                elif allowed_subportfolios:
                    cursor.execute(
                        """
                        SELECT id, code FROM public.projects
                         WHERE subportfolio_id = ANY(%s)
                        """,
                        (list(allowed_subportfolios),),
                    )
                    for row in cursor.fetchall():
                        allowed_projects.add(row[0])
                        if len(row) > 1 and row[1]:
                            allowed_project_codes.add(str(row[1]).casefold())

            return AccessContext(
                user_id=_uuid(user_id),
                auth_subject=auth_subject,
                role_name=str(role_name),
                allowed_subportfolio_ids=frozenset(
                    _uuid(value) for value in allowed_subportfolios
                ),
                allowed_project_ids=frozenset(
                    _uuid(value) for value in allowed_projects
                ),
                can_read=any(grant.can_read for grant in grants),
                can_write=any(grant.can_write for grant in grants),
                can_export=any(grant.can_export for grant in grants),
                grants=grants,
                allowed_subportfolio_codes=frozenset(allowed_subportfolio_codes),
                allowed_project_codes=frozenset(allowed_project_codes),
                display_name=str(display_name),
                email=str(email),
            )
        finally:
            connection.close()


def resolve_access_context(
    authorization: str | None,
    *,
    verifier: TokenVerifier | None = None,
    repository: AccessRepository | None = None,
) -> AccessContext:
    """Resolve um cabecalho Bearer em um contexto de acesso confiavel."""

    access_token = _bearer_token(authorization)
    identity = (verifier or SupabaseAuthVerifier()).verify(access_token)
    return (repository or PostgresAccessRepository()).resolve(identity.subject)


def authenticate_persona(
    profile_key: ProfileKey,
    password: str,
    *,
    authenticator: SupabasePasswordAuthenticator | None = None,
    verifier: TokenVerifier | None = None,
    repository: AccessRepository | None = None,
) -> PasswordLoginResponse:
    """Autentica a conta fixa da persona e confirma seu perfil no domínio."""

    try:
        password_authenticator = authenticator or SupabasePasswordAuthenticator()
    except RuntimeError as error:
        raise AuthenticationUnavailableError() from error
    access_token = password_authenticator.sign_in(
        PERSONA_EMAILS[profile_key],
        password,
    )
    context = resolve_access_context(
        f"Bearer {access_token}",
        verifier=verifier,
        repository=repository,
    )
    profile = access_profile_from_context(context)
    if profile.profile_key != profile_key:
        raise InvalidCredentialsError()
    return PasswordLoginResponse(access_token=access_token, profile=profile)


def authorize_operation(
    context: AccessContext,
    operation: AccessOperation,
    *,
    project_id: str | UUID | None = None,
    subportfolio_id: str | UUID | None = None,
    correlation_id: str | None = None,
) -> None:
    """Autoriza uma operacao usando somente regras resolvidas no servidor."""

    permitted = {
        "read": context.can_read,
        "write": context.can_write,
        "export": context.can_export,
    }[operation]
    project_reference = str(project_id).casefold() if project_id is not None else None
    subportfolio_reference = (
        str(subportfolio_id).casefold() if subportfolio_id is not None else None
    )
    allowed_projects = {
        *(str(value).casefold() for value in context.allowed_project_ids),
        *context.allowed_project_codes,
    }
    allowed_subportfolios = {
        *(str(value).casefold() for value in context.allowed_subportfolio_ids),
        *context.allowed_subportfolio_codes,
    }
    portfolio_access = any(
        grant.permission_scope == "portfolio" for grant in context.grants
    )
    if (
        not permitted
        or (
            not portfolio_access
            and project_reference is not None
            and project_reference not in allowed_projects
        )
        or (
            not portfolio_access
            and
            subportfolio_reference is not None
            and subportfolio_reference not in allowed_subportfolios
        )
    ):
        raise OutOfScopeForProfileError(
            operation,
            project_id=str(project_id) if project_id is not None else None,
            subportfolio_id=(
                str(subportfolio_id) if subportfolio_id is not None else None
            ),
            correlation_id=correlation_id,
        )


def authorize_message_scope(
    context: AccessContext,
    message: str,
    *,
    operation: AccessOperation = "read",
    correlation_id: str | None = None,
) -> None:
    """Nega referencias explicitas a projetos antes de qualquer recuperacao."""

    authorize_operation(context, operation, correlation_id=correlation_id)
    for project_code in sorted(set(PROJECT_REFERENCE_PATTERN.findall(message))):
        authorize_operation(
            context,
            operation,
            project_id=project_code,
            correlation_id=correlation_id,
        )


def access_profile_from_context(context: AccessContext) -> AccessProfileResponse:
    """Remove identificadores internos e descreve apenas o escopo do usuario."""

    profile_key = PROFILE_KEYS.get(context.role_name)
    if profile_key is None:
        raise AccessProfileNotConfiguredError()
    if any(grant.permission_scope == "portfolio" for grant in context.grants):
        scope_label = "Portfólio completo"
    elif context.allowed_subportfolio_codes:
        code = sorted(context.allowed_subportfolio_codes)[0].upper()
        scope_label = f"Subportfólio {code}"
    elif context.allowed_project_codes:
        code = sorted(context.allowed_project_codes)[0].upper()
        scope_label = f"Projeto {code}"
    else:
        scope_label = "Escopo configurado"
    return AccessProfileResponse(
        display_name=context.display_name,
        email=context.email,
        role_name=context.role_name,
        profile_key=profile_key,
        scope_label=scope_label,
        can_read=context.can_read,
        can_write=context.can_write,
        can_export=context.can_export,
    )


def audit_authorization_denial(
    context: AccessContext,
    denial: OutOfScopeForProfileError,
    *,
    component: str = "api",
    connect: Callable[..., Any] | None = None,
) -> None:
    """Registra a negativa sem permitir que falhas de auditoria abram acesso."""

    try:
        connection = open_database_connection(connect=connect)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.audit_events (
                        event_type, component, event_status, user_id,
                        correlation_id, event_payload
                    ) VALUES (%s, %s, 'bloqueado', %s, %s, %s::jsonb)
                    """,
                    (
                        "authorization.access_denied",
                        component,
                        context.user_id,
                        denial.correlation_id,
                        json.dumps(
                            {
                                "code": denial.code,
                                "operation": denial.operation,
                                "project_id": denial.project_id,
                                "subportfolio_id": denial.subportfolio_id,
                            },
                            ensure_ascii=False,
                        ),
                    ),
                )
            commit = getattr(connection, "commit", None)
            if commit:
                commit()
        finally:
            connection.close()
    except Exception as error:
        logger.warning(
            "Falha controlada ao registrar bloqueio de autorizacao: %s",
            type(error).__name__,
            extra={"correlation_id": denial.correlation_id},
        )


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.strip():
        raise AuthenticationRequiredError()
    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].casefold() != "bearer" or not parts[1]:
        raise InvalidAccessTokenError()
    return parts[1]


def _public_api_key() -> str:
    for name in PUBLIC_KEY_ENV_NAMES:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _is_privileged_key(api_key: str) -> bool:
    if api_key.startswith("sb_secret_"):
        return True
    parts = api_key.split(".")
    if len(parts) != 3:
        return False
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
    except (binascii.Error, ValueError, TypeError, json.JSONDecodeError):
        return False
    return isinstance(claims, dict) and claims.get("role") == "service_role"


def _grant_from_row(row: tuple[Any, ...]) -> AccessGrant:
    return AccessGrant(
        permission_scope=str(row[0]),
        subportfolio_id=_uuid(row[1]) if row[1] is not None else None,
        project_id=_uuid(row[2]) if row[2] is not None else None,
        can_read=bool(row[3]),
        can_write=bool(row[4]),
        can_export=bool(row[5]),
        subportfolio_code=str(row[6]) if len(row) > 6 and row[6] else None,
        project_code=str(row[7]) if len(row) > 7 and row[7] else None,
    )


def _uuid(value: Any) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))
