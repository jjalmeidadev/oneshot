"""Testes da carga idempotente de identidades e acessos da S5-03."""

from __future__ import annotations

from copy import deepcopy
import json
from uuid import uuid4

import httpx
import pytest

try:
    from scripts.seed_mvp_access import IDENTITIES, resolve_auth_users, run_seed
except ImportError:  # Execucao do pytest a partir da raiz do repositorio.
    from src.backend.scripts.seed_mvp_access import (
        IDENTITIES,
        resolve_auth_users,
        SupabaseAuthAdmin,
        run_seed,
    )
else:
    from scripts.seed_mvp_access import SupabaseAuthAdmin


class FakeAuthAdmin:
    def __init__(self) -> None:
        self.users: dict[str, dict] = {}
        self.create_calls = 0

    def find_user_by_email(self, email: str) -> dict | None:
        return self.users.get(email.casefold())

    def create_user(self, email: str, password: str) -> dict:
        assert password
        self.create_calls += 1
        user = {"id": str(uuid4()), "email": email}
        self.users[email.casefold()] = user
        return user


class FakeRepository:
    def __init__(self) -> None:
        self.public_users: dict[str, dict] = {}
        self.rules: dict[tuple, dict] = {}
        self.demo_subportfolio = False
        self.demo_project = False
        self.write_calls = 0

    def inspect(self, auth_users: dict[str, dict | None]) -> dict:
        return self._status(auth_users)

    def upsert_all(self, auth_users: dict[str, dict]) -> dict:
        self.write_calls += 1
        self.demo_subportfolio = True
        self.demo_project = True
        for spec in IDENTITIES:
            auth_user = auth_users[spec.key]
            self.public_users[spec.email] = {
                "entra_object_id": auth_user["id"],
                "role_name": spec.role_name,
            }
            key = (spec.email, spec.permission_scope, spec.target_code)
            self.rules[key] = {
                "can_read": spec.can_read,
                "can_write": spec.can_write,
                "can_export": spec.can_export,
            }
        return self._status(auth_users)

    def _status(self, auth_users: dict[str, dict | None]) -> dict:
        return {
            "auth_users": sum(value is not None for value in auth_users.values()),
            "public_users": len(self.public_users),
            "access_rules": len(self.rules),
            "demo_subportfolio": self.demo_subportfolio,
            "demo_project": self.demo_project,
            "reference_targets": 3,
        }


@pytest.fixture
def passwords(monkeypatch):
    monkeypatch.setenv("MVP_AUTH_PASSWORD", "segredo-apenas-do-teste")


def test_dry_run_nao_cria_identidades_nem_escreve(passwords):
    auth = FakeAuthAdmin()
    repository = FakeRepository()

    result = run_seed(auth, repository, dry_run=True)

    assert result["mode"] == "dry-run"
    assert result["auth"] == {"existing": 0, "created": 0, "would_create": 4}
    assert auth.create_calls == 0
    assert repository.write_calls == 0


def test_duas_execucoes_nao_duplicam_recursos(passwords):
    auth = FakeAuthAdmin()
    repository = FakeRepository()

    first = run_seed(auth, repository, dry_run=False)
    first_snapshot = deepcopy(first["database"])
    second = run_seed(auth, repository, dry_run=False)

    assert first["auth"]["created"] == 4
    assert second["auth"] == {"existing": 4, "created": 0, "would_create": 0}
    assert auth.create_calls == 4
    assert first_snapshot == second["database"]
    assert second["database"] == {
        "auth_users": 4,
        "public_users": 4,
        "access_rules": 4,
        "demo_subportfolio": True,
        "demo_project": True,
        "reference_targets": 3,
    }


def test_matriz_de_permissoes_e_escopos(passwords):
    auth = FakeAuthAdmin()
    repository = FakeRepository()
    run_seed(auth, repository, dry_run=False)

    assert repository.rules[(IDENTITIES[0].email, "portfolio", None)] == {
        "can_read": True,
        "can_write": False,
        "can_export": True,
    }
    assert repository.rules[(IDENTITIES[1].email, "subportfolio", "MOD")] == {
        "can_read": True,
        "can_write": False,
        "can_export": True,
    }
    assert repository.rules[(IDENTITIES[2].email, "projeto", "PRJ-0442")][
        "can_write"
    ] is True
    assert repository.rules[(IDENTITIES[3].email, "projeto", "PRJ-0510")] == {
        "can_read": True,
        "can_write": False,
        "can_export": False,
    }


def test_senha_especifica_tem_precedencia(monkeypatch):
    class PasswordCapturingAuth(FakeAuthAdmin):
        def __init__(self):
            super().__init__()
            self.passwords = []

        def create_user(self, email: str, password: str) -> dict:
            self.passwords.append((email, password))
            return super().create_user(email, password)

    monkeypatch.setenv("MVP_AUTH_PASSWORD", "compartilhada")
    monkeypatch.setenv("MVP_AUTH_PMO_PASSWORD", "especifica-pmo")
    auth = PasswordCapturingAuth()

    resolve_auth_users(auth, create=True)

    assert auth.passwords[0][1] == "especifica-pmo"
    assert all(password for _, password in auth.passwords)


def test_aplicacao_sem_senha_falha_antes_de_criar(monkeypatch):
    monkeypatch.delenv("MVP_AUTH_PASSWORD", raising=False)
    for spec in IDENTITIES:
        monkeypatch.delenv(spec.password_env, raising=False)
    auth = FakeAuthAdmin()

    with pytest.raises(RuntimeError, match="MVP_AUTH_PMO_PASSWORD"):
        resolve_auth_users(auth, create=True)

    assert auth.create_calls == 0


def test_cliente_admin_usa_endpoint_oficial_sem_metadados_de_autorizacao():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"users": []})
        return httpx.Response(
            200,
            json={"id": "auth-user-id", "email": IDENTITIES[0].email},
        )

    client = SupabaseAuthAdmin(
        "https://lykmrtukumqfdrwqkjzq.supabase.co",
        "service-key-de-teste",
        transport=httpx.MockTransport(handler),
    )
    try:
        assert client.find_user_by_email(IDENTITIES[0].email) is None
        created = client.create_user(IDENTITIES[0].email, "senha-do-teste")
    finally:
        client.close()

    assert created["id"] == "auth-user-id"
    assert requests[0].url.path == "/auth/v1/admin/users"
    assert requests[1].url.path == "/auth/v1/admin/users"
    payload = json.loads(requests[1].content)
    assert payload == {
        "email": IDENTITIES[0].email,
        "password": "senha-do-teste",
        "email_confirm": True,
    }
    assert "user_metadata" not in payload
    assert "app_metadata" not in payload
