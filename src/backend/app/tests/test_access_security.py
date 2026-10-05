"""Testes unitarios da autenticacao e resolucao central de acesso."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import json
from uuid import UUID

import httpx
import pytest
from fastapi.testclient import TestClient

from app.gemini.schemas import GeminiChatResponse
from app.main import app
from app.security import (
    AccessGrant,
    AccessContext,
    AccessProfileNotConfiguredError,
    AuthenticationUnavailableError,
    AuthenticationRequiredError,
    InvalidCredentialsError,
    InvalidAccessTokenError,
    PasswordLoginResponse,
    PostgresAccessRepository,
    SupabasePasswordAuthenticator,
    SupabaseAuthVerifier,
    UserInactiveError,
    OutOfScopeForProfileError,
    audit_authorization_denial,
    access_profile_from_context,
    authenticate_persona,
    authorize_message_scope,
    authorize_operation,
    get_access_context,
    resolve_access_context,
)


AUTH_SUBJECT = UUID("762a2bde-87b8-413f-8656-958a2f380574")
PUBLIC_USER_ID = UUID("6e7d0df0-c96a-4076-b241-64f78a05997a")
MOD_ID = UUID("4e8ef904-d4e5-401d-a78e-9144ec9b04f3")
PROJECT_0442_ID = UUID("fe091a56-310d-4465-8a13-5940d5765e1e")
PROJECT_0510_ID = UUID("3162119e-f361-4907-9358-6d32a4e91909")
DEMO_SUBPORTFOLIO_ID = UUID("cf659f07-a94d-5370-94f2-b1f628a8e8ad")
DEMO_PROJECT_ID = UUID("5f156c3e-b806-535f-b9f8-3131e5c91f72")


class CursorDouble:
    def __init__(self, user, rules, subportfolios=(), projects=()):
        self.user = user
        self.rules = list(rules)
        self.subportfolios = list(subportfolios)
        self.projects = list(projects)
        self.result = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, query, _params=None):
        normalized = " ".join(query.split())
        if "FROM public.users" in normalized:
            self.result = [] if self.user is None else [self.user]
        elif "FROM public.access_rules" in normalized:
            self.result = self.rules
        elif "FROM public.subportfolios" in normalized:
            self.result = [(item,) for item in self.subportfolios]
        elif "FROM public.projects p" in normalized:
            self.result = [(item,) for item in self.projects]
        elif "FROM public.projects" in normalized:
            self.result = [(item,) for item in self.projects]
        else:  # pragma: no cover - protege o double contra SQL novo sem teste.
            raise AssertionError(f"Consulta inesperada: {normalized}")

    def fetchone(self):
        return self.result[0] if self.result else None

    def fetchall(self):
        return list(self.result)


class ConnectionDouble:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


def repository(user, rules, subportfolios=(), projects=()):
    connection = ConnectionDouble(
        CursorDouble(user, rules, subportfolios, projects)
    )
    return PostgresAccessRepository(lambda: connection), connection


@dataclass
class VerifierDouble:
    identity: object

    def verify(self, _access_token):
        if isinstance(self.identity, Exception):
            raise self.identity
        return self.identity


@dataclass
class IdentityDouble:
    subject: UUID


@dataclass
class RepositoryDouble:
    result: object

    def resolve(self, _auth_subject):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@dataclass
class PasswordAuthenticatorDouble:
    access_token: str = "jwt-gerado"
    email: str | None = None
    password: str | None = None

    def sign_in(self, email, password):
        self.email = email
        self.password = password
        return self.access_token


def base_context(role_name="pmo"):
    return AccessContext(
        user_id=PUBLIC_USER_ID,
        auth_subject=AUTH_SUBJECT,
        role_name=role_name,
        allowed_subportfolio_ids=frozenset(),
        allowed_project_ids=frozenset(),
        can_read=True,
        can_write=False,
        can_export=True,
        grants=(),
        display_name="[DEMO] PMO",
        email="mvp.pmo@oneshot.example.com",
    )


def scoped_context(
    role_name,
    *,
    scope,
    project_codes=(),
    subportfolio_codes=(),
    can_write=False,
    can_export=False,
    display_name="Usuario MVP",
    email="usuario@oneshot.example.com",
):
    return AccessContext(
        user_id=PUBLIC_USER_ID,
        auth_subject=AUTH_SUBJECT,
        role_name=role_name,
        allowed_subportfolio_ids=frozenset(),
        allowed_project_ids=frozenset(),
        can_read=True,
        can_write=can_write,
        can_export=can_export,
        grants=(
            AccessGrant(
                scope,
                None,
                None,
                True,
                can_write,
                can_export,
            ),
        ),
        allowed_subportfolio_codes=frozenset(
            value.casefold() for value in subportfolio_codes
        ),
        allowed_project_codes=frozenset(
            value.casefold() for value in project_codes
        ),
        display_name=display_name,
        email=email,
    )


def test_token_valido_e_role_do_cliente_ignorado():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": str(AUTH_SUBJECT),
                "user_metadata": {"role": "admin", "can_write": True},
            },
        )

    verifier = SupabaseAuthVerifier(
        "https://lykmrtukumqfdrwqkjzq.supabase.co",
        "sb_publishable_test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    context = resolve_access_context(
        "Bearer token-valido",
        verifier=verifier,
        repository=RepositoryDouble(base_context(role_name="pmo")),
    )

    assert context.role_name == "pmo"
    assert requests[0].url.path == "/auth/v1/user"
    assert requests[0].headers["authorization"] == "Bearer token-valido"
    assert requests[0].headers["apikey"] == "sb_publishable_test"


def test_login_por_persona_mapeia_email_e_confirma_perfil():
    authenticator = PasswordAuthenticatorDouble()

    response = authenticate_persona(
        "pmo",
        "senha-digitada",
        authenticator=authenticator,
        verifier=VerifierDouble(IdentityDouble(AUTH_SUBJECT)),
        repository=RepositoryDouble(base_context()),
    )

    assert authenticator.email == "mvp.pmo@oneshot.example.com"
    assert authenticator.password == "senha-digitada"
    assert response.access_token == "jwt-gerado"
    assert response.profile.profile_key == "pmo"


def test_login_recusa_conta_que_nao_corresponde_a_persona():
    with pytest.raises(InvalidCredentialsError):
        authenticate_persona(
            "pmo",
            "senha-digitada",
            authenticator=PasswordAuthenticatorDouble(),
            verifier=VerifierDouble(IdentityDouble(AUTH_SUBJECT)),
            repository=RepositoryDouble(base_context(role_name="consulta")),
        )


def test_login_supabase_traduz_senha_invalida_sem_expor_resposta():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(400, json={"error_description": "detalhe privado"})

    authenticator = SupabasePasswordAuthenticator(
        "https://lykmrtukumqfdrwqkjzq.supabase.co",
        "sb_publishable_test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(InvalidCredentialsError) as error:
        authenticator.sign_in("mvp.pmo@oneshot.example.com", "senha-incorreta")

    assert error.value.code == "INVALID_CREDENTIALS"
    assert "privado" not in error.value.message
    assert requests[0].url.path == "/auth/v1/token"
    assert requests[0].url.params["grant_type"] == "password"
    assert requests[0].headers["apikey"] == "sb_publishable_test"
    assert json.loads(requests[0].content) == {
        "email": "mvp.pmo@oneshot.example.com",
        "password": "senha-incorreta",
    }


def test_login_supabase_traduz_indisponibilidade():
    authenticator = SupabasePasswordAuthenticator(
        "https://lykmrtukumqfdrwqkjzq.supabase.co",
        "sb_publishable_test",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(503, json={"message": "offline"})
            )
        ),
    )

    with pytest.raises(AuthenticationUnavailableError) as error:
        authenticator.sign_in("mvp.pmo@oneshot.example.com", "senha")

    assert error.value.status_code == 503


def test_token_ausente():
    with pytest.raises(AuthenticationRequiredError) as error:
        resolve_access_context(None)
    assert error.value.status_code == 401
    assert error.value.code == "AUTHENTICATION_REQUIRED"


def test_token_invalido():
    verifier = SupabaseAuthVerifier(
        "https://lykmrtukumqfdrwqkjzq.supabase.co",
        "sb_publishable_test",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(401, json={"message": "invalid"})
            )
        ),
    )
    with pytest.raises(InvalidAccessTokenError) as error:
        resolve_access_context(
            "Bearer invalido",
            verifier=verifier,
            repository=RepositoryDouble(base_context()),
        )
    assert error.value.status_code == 401
    assert error.value.code == "INVALID_ACCESS_TOKEN"


def test_esquema_de_autorizacao_invalido():
    with pytest.raises(InvalidAccessTokenError):
        resolve_access_context("Basic credencial")


def test_usuario_nao_mapeado():
    repo, connection = repository(None, [])
    with pytest.raises(AccessProfileNotConfiguredError) as error:
        resolve_access_context(
            "Bearer token",
            verifier=VerifierDouble(IdentityDouble(AUTH_SUBJECT)),
            repository=repo,
        )
    assert error.value.code == "ACCESS_PROFILE_NOT_CONFIGURED"
    assert error.value.status_code == 403
    assert connection.closed


def test_usuario_inativo():
    repo, connection = repository(
        (
            PUBLIC_USER_ID,
            "[DEMO] PMO",
            "mvp.pmo@oneshot.example.com",
            "pmo",
            False,
        ),
        [],
    )
    with pytest.raises(UserInactiveError) as error:
        resolve_access_context(
            "Bearer token",
            verifier=VerifierDouble(IdentityDouble(AUTH_SUBJECT)),
            repository=repo,
        )
    assert error.value.code == "USER_INACTIVE"
    assert error.value.status_code == 403
    assert connection.closed


def test_usuario_sem_regra_ativa():
    repo, _ = repository(
        (
            PUBLIC_USER_ID,
            "[DEMO] PMO",
            "mvp.pmo@oneshot.example.com",
            "pmo",
            True,
        ),
        [],
    )
    with pytest.raises(AccessProfileNotConfiguredError):
        repo.resolve(AUTH_SUBJECT)


@pytest.mark.parametrize(
    (
        "role_name",
        "rules",
        "subportfolios",
        "projects",
        "expected_subportfolios",
        "expected_projects",
        "expected_permissions",
    ),
    [
        (
            "pmo",
            [("portfolio", None, None, True, False, True)],
            [MOD_ID, DEMO_SUBPORTFOLIO_ID],
            [PROJECT_0442_ID, PROJECT_0510_ID, DEMO_PROJECT_ID],
            {MOD_ID, DEMO_SUBPORTFOLIO_ID},
            {PROJECT_0442_ID, PROJECT_0510_ID, DEMO_PROJECT_ID},
            (True, False, True),
        ),
        (
            "lider_subportfolio",
            [("subportfolio", MOD_ID, None, True, False, True)],
            [],
            [PROJECT_0442_ID, PROJECT_0510_ID],
            {MOD_ID},
            {PROJECT_0442_ID, PROJECT_0510_ID},
            (True, False, True),
        ),
        (
            "equipe_projeto",
            [("projeto", None, PROJECT_0442_ID, True, True, True)],
            [],
            [],
            set(),
            {PROJECT_0442_ID},
            (True, True, True),
        ),
        (
            "consulta",
            [("projeto", None, PROJECT_0510_ID, True, False, False)],
            [],
            [],
            set(),
            {PROJECT_0510_ID},
            (True, False, False),
        ),
    ],
)
def test_regras_corretas_para_os_quatro_perfis(
    role_name,
    rules,
    subportfolios,
    projects,
    expected_subportfolios,
    expected_projects,
    expected_permissions,
):
    repo, connection = repository(
        (
            PUBLIC_USER_ID,
            f"[DEMO] {role_name}",
            f"{role_name}@oneshot.example.com",
            role_name,
            True,
        ),
        rules,
        subportfolios,
        projects,
    )

    context = repo.resolve(AUTH_SUBJECT)

    assert context.role_name == role_name
    assert context.auth_subject == AUTH_SUBJECT
    assert context.user_id == PUBLIC_USER_ID
    assert context.allowed_subportfolio_ids == frozenset(expected_subportfolios)
    assert context.allowed_project_ids == frozenset(expected_projects)
    assert (context.can_read, context.can_write, context.can_export) == expected_permissions
    assert context.display_name == f"[DEMO] {role_name}"
    assert context.email == f"{role_name}@oneshot.example.com"
    assert connection.closed


@pytest.mark.parametrize(
    "api_key",
    [
        "sb_secret_nao_permitida",
        ".".join(
            (
                "cabecalho",
                base64.urlsafe_b64encode(
                    json.dumps({"role": "service_role"}).encode()
                )
                .decode()
                .rstrip("="),
                "assinatura",
            )
        ),
    ],
)
def test_chave_privilegiada_e_rejeitada_mesmo_se_passada_como_publicavel(api_key):
    with pytest.raises(RuntimeError, match="nunca uma secret/service role"):
        SupabaseAuthVerifier(
            "https://lykmrtukumqfdrwqkjzq.supabase.co",
            api_key,
        )


def test_matriz_operacional_dos_quatro_perfis():
    pmo = scoped_context(
        "pmo", scope="portfolio", can_export=True
    )
    leader = scoped_context(
        "lider_subportfolio",
        scope="subportfolio",
        project_codes=("PRJ-0442", "PRJ-0510"),
        subportfolio_codes=("MOD",),
        can_export=True,
    )
    manager = scoped_context(
        "equipe_projeto",
        scope="projeto",
        project_codes=("PRJ-0442",),
        can_write=True,
        can_export=True,
    )
    consulta = scoped_context(
        "consulta", scope="projeto", project_codes=("PRJ-0510",)
    )

    authorize_operation(pmo, "read", project_id="PRJ-0442")
    authorize_operation(pmo, "read", project_id="S5-03-DEMO-PROJECT")
    authorize_operation(pmo, "export", project_id="PRJ-0442")
    with pytest.raises(OutOfScopeForProfileError):
        authorize_operation(pmo, "write", project_id="PRJ-0442")

    authorize_operation(leader, "read", subportfolio_id="MOD")
    with pytest.raises(OutOfScopeForProfileError):
        authorize_operation(
            leader, "read", subportfolio_id="S5-03-DEMO-SUBPORTFOLIO"
        )

    authorize_operation(manager, "read", project_id="PRJ-0442")
    authorize_operation(manager, "write", project_id="PRJ-0442")
    with pytest.raises(OutOfScopeForProfileError):
        authorize_operation(manager, "read", project_id="PRJ-0510")

    authorize_operation(consulta, "read", project_id="PRJ-0510")
    with pytest.raises(OutOfScopeForProfileError):
        authorize_operation(consulta, "export", project_id="PRJ-0510")
    with pytest.raises(OutOfScopeForProfileError):
        authorize_operation(consulta, "write", project_id="PRJ-0510")


def test_referencia_explicita_fora_do_escopo_e_negada_antes_da_recuperacao():
    manager = scoped_context(
        "equipe_projeto",
        scope="projeto",
        project_codes=("PRJ-0442",),
        can_write=True,
        can_export=True,
    )

    with pytest.raises(OutOfScopeForProfileError) as error:
        authorize_message_scope(manager, "Mostre o andamento do PRJ-0510")

    assert error.value.code == "OUT_OF_SCOPE_FOR_PROFILE"
    assert "PRJ-0510" not in error.value.message

    with pytest.raises(OutOfScopeForProfileError):
        authorize_message_scope(
            manager, "Mostre o projeto S5-03-DEMO-PROJECT"
        )


class AuditCursorDouble:
    def __init__(self):
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, query, params):
        self.query = " ".join(query.split())
        self.params = params


class AuditConnectionDouble:
    def __init__(self):
        self.cursor_double = AuditCursorDouble()
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_double

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


def test_auditoria_de_negacao_recebe_user_id_e_status_bloqueado(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test.invalid/postgres")
    connection = AuditConnectionDouble()
    denial = OutOfScopeForProfileError(
        "read", project_id="PRJ-0510", correlation_id="correlation-258"
    )

    audit_authorization_denial(
        base_context(),
        denial,
        connect=lambda *_args, **_kwargs: connection,
    )

    assert "'bloqueado'" in connection.cursor_double.query
    assert connection.cursor_double.params[2] == PUBLIC_USER_ID
    assert connection.cursor_double.params[3] == "correlation-258"
    payload = json.loads(connection.cursor_double.params[4])
    assert payload == {
        "code": "OUT_OF_SCOPE_FOR_PROFILE",
        "operation": "read",
        "project_id": "PRJ-0510",
        "subportfolio_id": None,
    }
    assert connection.committed and connection.closed


def test_rota_protegida_sem_token_retorna_authentication_required():
    app.dependency_overrides.pop(get_access_context, None)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/chat",
                json={"message": "status do PRJ-0442", "use_intent_classifier": False},
            )
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_rota_protegida_com_token_invalido_retorna_invalid_access_token():
    def invalid_access():
        raise InvalidAccessTokenError()

    app.dependency_overrides[get_access_context] = invalid_access
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/chat",
                headers={"Authorization": "Bearer invalido"},
                json={"message": "status do PRJ-0442", "use_intent_classifier": False},
            )
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


def test_health_permanece_publico_mesmo_sem_contexto_autenticado():
    def must_not_resolve():
        pytest.fail("health nao deve resolver identidade")

    app.dependency_overrides[get_access_context] = must_not_resolve
    try:
        with TestClient(app) as client:
            response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 200


def test_pedido_negado_nao_chama_pipeline_rag_ou_llm(monkeypatch):
    manager = scoped_context(
        "equipe_projeto",
        scope="projeto",
        project_codes=("PRJ-0442",),
        can_write=True,
        can_export=True,
    )
    app.dependency_overrides[get_access_context] = lambda: manager
    calls = []
    monkeypatch.setattr(
        "app.main.process_message",
        lambda *_args, **_kwargs: calls.append("pipeline"),
    )
    monkeypatch.setattr("app.main.audit_request_denial", lambda *_args: None)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/chat",
                headers={"Authorization": "Bearer validado"},
                json={"message": "status do PRJ-0510", "use_intent_classifier": False},
            )
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "OUT_OF_SCOPE_FOR_PROFILE"
    assert calls == []


def test_access_me_rejeita_token_ausente():
    app.dependency_overrides.pop(get_access_context, None)
    try:
        with TestClient(app) as client:
            response = client.get("/api/access/me")
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_access_login_e_publico_e_devolve_token_e_perfil(monkeypatch):
    expected = PasswordLoginResponse(
        access_token="jwt-gerado",
        profile=access_profile_from_context(base_context()),
    )
    calls = []

    def login(profile_key, password):
        calls.append((profile_key, password))
        return expected

    monkeypatch.setattr("app.main.authenticate_persona", login)
    with TestClient(app) as client:
        response = client.post(
            "/api/access/login",
            json={"profile_key": "pmo", "password": "senha-digitada"},
        )

    assert response.status_code == 200
    assert response.json() == expected.model_dump()
    assert response.headers["cache-control"] == "no-store"
    assert calls == [("pmo", "senha-digitada")]


def test_access_login_rejeita_entrada_incompleta_com_erro_controlado():
    with TestClient(app) as client:
        response = client.post(
            "/api/access/login",
            json={"profile_key": "pmo", "password": ""},
        )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "INVALID_INPUT",
            "message": "Selecione uma persona e informe a senha.",
        }
    }


def test_access_me_rejeita_token_invalido():
    app.dependency_overrides[get_access_context] = lambda: (_ for _ in ()).throw(
        InvalidAccessTokenError()
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/access/me",
                headers={"Authorization": "Bearer invalido"},
            )
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


@pytest.mark.parametrize(
    ("context", "expected_profile", "expected_scope"),
    [
        (
            scoped_context(
                "pmo",
                scope="portfolio",
                can_export=True,
                display_name="[DEMO] PMO",
                email="mvp.pmo@oneshot.example.com",
            ),
            "pmo",
            "Portfólio completo",
        ),
        (
            scoped_context(
                "lider_subportfolio",
                scope="subportfolio",
                subportfolio_codes=("MOD",),
                can_export=True,
                display_name="[DEMO] Lider de Subportfolio",
                email="mvp.lider-subportfolio@oneshot.example.com",
            ),
            "lider_subportfolio",
            "Subportfólio MOD",
        ),
        (
            scoped_context(
                "equipe_projeto",
                scope="projeto",
                project_codes=("PRJ-0442",),
                can_write=True,
                can_export=True,
                display_name="[DEMO] Gerente de Projeto",
                email="mvp.gerente-projeto@oneshot.example.com",
            ),
            "gerente_projeto",
            "Projeto PRJ-0442",
        ),
        (
            scoped_context(
                "consulta",
                scope="projeto",
                project_codes=("PRJ-0510",),
                display_name="[DEMO] Consulta",
                email="mvp.consulta@oneshot.example.com",
            ),
            "consulta",
            "Projeto PRJ-0510",
        ),
    ],
)
def test_access_me_retorna_somente_perfil_atual(
    context,
    expected_profile,
    expected_scope,
):
    app.dependency_overrides[get_access_context] = lambda: context
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/access/me",
                headers={"Authorization": "Bearer validado"},
            )
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 200
    assert response.json() == {
        "display_name": context.display_name,
        "email": context.email,
        "role_name": context.role_name,
        "profile_key": expected_profile,
        "scope_label": expected_scope,
        "can_read": context.can_read,
        "can_write": context.can_write,
        "can_export": context.can_export,
    }
    serialized = response.text.casefold()
    assert "auth_subject" not in serialized
    assert "user_id" not in serialized
    assert "service_role" not in serialized
    assert "validado" not in serialized


# ==========================================================================
# Ajustes da revisao do MR (S5-03/S5-04)
# ==========================================================================


def _rotas_que_exigem(dependencia):
    from fastapi.routing import APIRoute

    def dependencias(dependant):
        for sub in dependant.dependencies:
            yield sub.call
            yield from dependencias(sub)

    from app.alerts.router import router as alerts_router
    from app.reports.router import router as reports_router

    # Os routers incluidos nao aparecem achatados em `app.routes` nesta versao
    # do FastAPI; as rotas sao lidas de cada router de origem.
    rotas = [*app.routes, *alerts_router.routes, *reports_router.routes]
    return {
        (route.path, method)
        for route in rotas
        if isinstance(route, APIRoute)
        for method in route.methods
        if dependencia in set(dependencias(route.dependant))
    }


def test_proatividade_e_alertas_exigem_leitura_e_nao_escrita():
    """A sugestao so analisa, e alerta e preferencia do proprio usuario."""

    from app.security import require_read_access, require_write_access

    escrita = _rotas_que_exigem(require_write_access)
    leitura = _rotas_que_exigem(require_read_access)

    assert ("/api/chat/proactive-confirmation", "POST") in leitura
    assert not any(path.startswith("/api/alert") for path, _ in escrita)
    assert not any(path.startswith("/api/notifications") for path, _ in escrita)
    assert ("/api/chat/proactive-confirmation", "POST") not in escrita
    assert ("/api/alert-workflow-sessions", "POST") in leitura


def test_perfil_sem_escrita_aceita_sugestao_proativa(monkeypatch):
    from app.gemini.schemas import ProactiveConfirmationResponse

    consulta = scoped_context("consulta", scope="projeto", project_codes=("PRJ-0510",))
    app.dependency_overrides[get_access_context] = lambda: consulta
    monkeypatch.setattr(
        "app.main.process_proactive_confirmation",
        lambda *_a, **_k: ProactiveConfirmationResponse(status="declined"),
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/chat/proactive-confirmation",
                headers={"Authorization": "Bearer validado"},
                json={
                    "suggestion_id": "00000000-0000-0000-0000-000000000250",
                    "conversation_id": "conversa",
                    "decision": "decline",
                },
            )
    finally:
        app.dependency_overrides.pop(get_access_context, None)

    assert response.status_code == 200


def test_documento_institucional_vale_para_todos_os_perfis():
    """Documento sem projeto (procedimento, comunicado) nao e escopo de ninguem."""

    from app.rag.sharepoint import SharePointDocument, retrieve_sharepoint_context

    def documento(source_id, project_id=None, project_code=None):
        return SharePointDocument(
            source_id=source_id,
            title="Procedimento de objeto perdido",
            list_name="Procedimentos",
            content="Objeto perdido deve ser entregue no balcao de atendimento.",
            web_url="https://mock.sharepoint.local/item",
            last_modified="2026-09-09T12:00:00Z",
            search_text="objeto perdido balcao atendimento",
            project_id=project_id,
            project_code=project_code,
        )

    documentos = [
        documento("institucional:1"),
        documento("projeto:0442", str(PROJECT_0442_ID), "PRJ-0442"),
        documento("projeto:0510", str(PROJECT_0510_ID), "PRJ-0510"),
    ]

    resultado = retrieve_sharepoint_context(
        "objeto perdido",
        documents=documentos,
        allowed_project_ids={"prj-0510"},
    )

    assert {r.document.source_id for r in resultado} == {
        "institucional:1",
        "projeto:0510",
    }


def test_consulta_sql_aceita_documento_sem_projeto():
    from app.rag.database import RAG_DATABASE_QUERY

    sem_comentarios = "\n".join(
        linha.split("--")[0] for linha in RAG_DATABASE_QUERY.splitlines()
    )
    filtro = " ".join(sem_comentarios.split())
    assert (
        "access.project_ids IS NULL "
        "OR COALESCE(se.project_id, a.project_id) IS NULL "
        "OR COALESCE(se.project_id, a.project_id) = ANY(access.project_ids)"
    ) in filtro


@pytest.mark.parametrize(
    "resposta",
    [
        httpx.ConnectError("Auth fora do ar"),
        httpx.Response(503, json={"message": "unavailable"}),
    ],
)
def test_queda_do_auth_nao_vira_token_invalido(resposta):
    def handler(_request: httpx.Request) -> httpx.Response:
        if isinstance(resposta, Exception):
            raise resposta
        return resposta

    verifier = SupabaseAuthVerifier(
        "https://lykmrtukumqfdrwqkjzq.supabase.co",
        "sb_publishable_test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(AuthenticationUnavailableError) as error:
        verifier.verify("token")
    assert error.value.status_code == 503


def test_revalidacao_de_relatorio_nega_usuario_inativo(monkeypatch):
    from app.reports.errors import ReportAccessDeniedError
    from app.reports.security import resolve_report_identity_by_subject

    monkeypatch.setenv(
        "REPORT_SIMULATED_IDENTITIES",
        json.dumps({"legado": {"subject": str(AUTH_SUBJECT), "can_export": True}}),
    )

    def inativo(_self, _subject):
        raise UserInactiveError()

    monkeypatch.setattr(PostgresAccessRepository, "resolve", inativo)

    with pytest.raises(ReportAccessDeniedError):
        resolve_report_identity_by_subject(str(AUTH_SUBJECT))
