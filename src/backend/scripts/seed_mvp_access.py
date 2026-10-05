"""Carrega identidades Auth e regras de acesso sinteticas do MVP (#257).

O schema ``auth`` e acessado exclusivamente pela Admin API oficial do
Supabase. Os dados publicos sao gravados em uma unica transacao PostgreSQL,
permitindo repetir o comando com seguranca depois de uma interrupcao.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid5

import httpx
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


EXPECTED_PROJECT_ID = "lykmrtukumqfdrwqkjzq"
AUTH_PAGE_SIZE = 1000
SEED_NAMESPACE = UUID("d882be20-f67c-5d15-9e36-a2db262bc347")
DEMO_SUBPORTFOLIO_ID = uuid5(SEED_NAMESPACE, "s5-03:subportfolio:negacao-cruzada")
DEMO_PROJECT_ID = uuid5(SEED_NAMESPACE, "s5-03:project:negacao-cruzada")
DEMO_SUBPORTFOLIO_CODE = "DEMO-ACESSO"
DEMO_SUBPORTFOLIO_SOURCE_ID = "S5-03-DEMO-SUBPORTFOLIO"
DEMO_PROJECT_CODE = "PRJ-DEMO-ACESSO"
DEMO_PROJECT_SOURCE_ID = "S5-03-DEMO-PROJECT"


@dataclass(frozen=True)
class IdentitySpec:
    key: str
    email: str
    display_name: str
    role_name: str
    password_env: str
    permission_scope: str
    target_code: str | None
    can_read: bool
    can_write: bool
    can_export: bool


IDENTITIES = (
    IdentitySpec(
        key="pmo",
        email="mvp.pmo@oneshot.example.com",
        display_name="[DEMO] PMO",
        role_name="pmo",
        password_env="MVP_AUTH_PMO_PASSWORD",
        permission_scope="portfolio",
        target_code=None,
        can_read=True,
        can_write=False,
        can_export=True,
    ),
    IdentitySpec(
        key="lider_subportfolio",
        email="mvp.lider-subportfolio@oneshot.example.com",
        display_name="[DEMO] Lider de Subportfolio",
        role_name="lider_subportfolio",
        password_env="MVP_AUTH_SUBPORTFOLIO_LEADER_PASSWORD",
        permission_scope="subportfolio",
        target_code="MOD",
        can_read=True,
        can_write=False,
        can_export=True,
    ),
    IdentitySpec(
        key="gerente_projeto",
        email="mvp.gerente-projeto@oneshot.example.com",
        display_name="[DEMO] Gerente de Projeto",
        role_name="equipe_projeto",
        password_env="MVP_AUTH_PROJECT_MANAGER_PASSWORD",
        permission_scope="projeto",
        target_code="PRJ-0442",
        can_read=True,
        can_write=True,
        can_export=True,
    ),
    IdentitySpec(
        key="consulta",
        email="mvp.consulta@oneshot.example.com",
        display_name="[DEMO] Consulta",
        role_name="consulta",
        password_env="MVP_AUTH_CONSULTA_PASSWORD",
        permission_scope="projeto",
        target_code="PRJ-0510",
        can_read=True,
        can_write=False,
        can_export=False,
    ),
)


class AuthAdmin(Protocol):
    def find_user_by_email(self, email: str) -> dict | None: ...

    def create_user(self, email: str, password: str) -> dict: ...


class AccessRepository(Protocol):
    def inspect(self, auth_users: dict[str, dict | None]) -> dict: ...

    def upsert_all(self, auth_users: dict[str, dict]) -> dict: ...


class SupabaseAuthAdmin:
    """Cliente minimo da Admin API; a service role nunca sai do processo."""

    def __init__(
        self,
        base_url: str,
        service_key: str,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/auth/v1/admin",
            headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
            },
            timeout=30,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def find_user_by_email(self, email: str) -> dict | None:
        page = 1
        wanted = email.casefold()
        while True:
            response = self._client.get(
                "/users", params={"page": page, "per_page": AUTH_PAGE_SIZE}
            )
            response.raise_for_status()
            payload = response.json()
            users = payload.get("users", payload if isinstance(payload, list) else [])
            for user in users:
                if str(user.get("email", "")).casefold() == wanted:
                    return user
            if len(users) < AUTH_PAGE_SIZE:
                return None
            page += 1

    def create_user(self, email: str, password: str) -> dict:
        response = self._client.post(
            "/users",
            json={"email": email, "password": password, "email_confirm": True},
        )
        if response.status_code in {409, 422}:
            existing = self.find_user_by_email(email)
            if existing is not None:
                return existing
        response.raise_for_status()
        return response.json()


class PostgresAccessRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def inspect(self, auth_users: dict[str, dict | None]) -> dict:
        with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                reference_ids = self._reference_ids(cursor)
                result = self._status(cursor, auth_users, reference_ids)
            connection.rollback()
        return result

    def upsert_all(self, auth_users: dict[str, dict]) -> dict:
        with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                reference_ids = self._reference_ids(cursor)
                self._upsert_demo_scope(cursor)
                public_user_ids = {
                    spec.key: self._upsert_public_user(cursor, spec, auth_users[spec.key])
                    for spec in IDENTITIES
                }
                for spec in IDENTITIES:
                    self._upsert_access_rule(
                        cursor, spec, public_user_ids[spec.key], reference_ids
                    )
                result = self._status(cursor, auth_users, reference_ids)
            connection.commit()
        return result

    @staticmethod
    def _reference_ids(cursor) -> dict[str, UUID]:
        cursor.execute(
            """
            SELECT 'subportfolio:MOD' AS target, id FROM public.subportfolios WHERE code = 'MOD'
            UNION ALL
            SELECT 'project:' || code AS target, id
              FROM public.projects WHERE code IN ('PRJ-0442', 'PRJ-0510')
            """
        )
        found = {row["target"]: row["id"] for row in cursor.fetchall()}
        expected = {"subportfolio:MOD", "project:PRJ-0442", "project:PRJ-0510"}
        missing = sorted(expected - found.keys())
        if missing:
            raise RuntimeError("Referencias obrigatorias ausentes: " + ", ".join(missing))
        return found

    @staticmethod
    def _upsert_demo_scope(cursor) -> None:
        cursor.execute(
            """
            INSERT INTO public.subportfolios (
                id, partner_source_id, code, title, description, is_active, metadata
            ) VALUES (
                %s, %s, %s, '[DEMO] Subportfolio para negacao cruzada',
                'Dado totalmente sintetico da S5-03 para provar isolamento de escopo.',
                TRUE, '{"synthetic": true, "seed": "s5-03", "purpose": "cross_scope_denial"}'::jsonb
            )
            ON CONFLICT (partner_source_id) DO UPDATE SET
                code = EXCLUDED.code,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                is_active = TRUE,
                metadata = public.subportfolios.metadata || EXCLUDED.metadata
            """,
            (DEMO_SUBPORTFOLIO_ID, DEMO_SUBPORTFOLIO_SOURCE_ID, DEMO_SUBPORTFOLIO_CODE),
        )
        cursor.execute(
            """
            INSERT INTO public.projects (
                id, subportfolio_id, partner_source_id, code, title, description,
                status, metadata
            ) VALUES (
                %s, %s, %s, %s, '[DEMO] Projeto para negacao cruzada',
                'Dado totalmente sintetico da S5-03 fora do subportfolio MOD.',
                'planejado',
                '{"synthetic": true, "seed": "s5-03", "purpose": "cross_scope_denial"}'::jsonb
            )
            ON CONFLICT (partner_source_id) DO UPDATE SET
                subportfolio_id = EXCLUDED.subportfolio_id,
                code = EXCLUDED.code,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                metadata = public.projects.metadata || EXCLUDED.metadata
            """,
            (
                DEMO_PROJECT_ID,
                DEMO_SUBPORTFOLIO_ID,
                DEMO_PROJECT_SOURCE_ID,
                DEMO_PROJECT_CODE,
            ),
        )

    @staticmethod
    def _upsert_public_user(cursor, spec: IdentitySpec, auth_user: dict) -> UUID:
        auth_id = str(auth_user.get("id", "")).strip()
        if not auth_id:
            raise RuntimeError(f"Admin API nao retornou id para o perfil {spec.key}.")
        cursor.execute(
            """
            SELECT id FROM public.users
             WHERE email = %s OR entra_object_id = %s
             FOR UPDATE
            """,
            (spec.email, auth_id),
        )
        rows = cursor.fetchall()
        if len(rows) > 1:
            raise RuntimeError(
                f"Conflito entre email e entra_object_id para o perfil {spec.key}."
            )
        metadata = json.dumps({"synthetic": True, "seed": "s5-03"})
        if rows:
            user_id = rows[0]["id"]
            cursor.execute(
                """
                UPDATE public.users
                   SET entra_object_id = %s, display_name = %s, email = %s,
                       role_name = %s, is_active = TRUE,
                       metadata = metadata || %s::jsonb
                 WHERE id = %s
                """,
                (auth_id, spec.display_name, spec.email, spec.role_name, metadata, user_id),
            )
            return user_id
        cursor.execute(
            """
            INSERT INTO public.users (
                entra_object_id, display_name, email, role_name, is_active, metadata
            ) VALUES (%s, %s, %s, %s, TRUE, %s::jsonb)
            RETURNING id
            """,
            (auth_id, spec.display_name, spec.email, spec.role_name, metadata),
        )
        return cursor.fetchone()["id"]

    @staticmethod
    def _upsert_access_rule(
        cursor, spec: IdentitySpec, user_id: UUID, reference_ids: dict[str, UUID]
    ) -> None:
        subportfolio_id = None
        project_id = None
        if spec.permission_scope == "subportfolio":
            subportfolio_id = reference_ids[f"subportfolio:{spec.target_code}"]
        elif spec.permission_scope == "projeto":
            project_id = reference_ids[f"project:{spec.target_code}"]
        cursor.execute(
            """
            INSERT INTO public.access_rules (
                user_id, role_name, subportfolio_id, project_id, permission_scope,
                can_read, can_write, can_export, is_active
            ) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (user_id, role_name, subportfolio_id, project_id, permission_scope)
            DO UPDATE SET
                can_read = EXCLUDED.can_read,
                can_write = EXCLUDED.can_write,
                can_export = EXCLUDED.can_export,
                is_active = TRUE
            """,
            (
                user_id,
                subportfolio_id,
                project_id,
                spec.permission_scope,
                spec.can_read,
                spec.can_write,
                spec.can_export,
            ),
        )

    @staticmethod
    def _status(cursor, auth_users, reference_ids) -> dict:
        emails = [spec.email for spec in IDENTITIES]
        cursor.execute(
            """
            SELECT email, id, entra_object_id, role_name
              FROM public.users WHERE email = ANY(%s)
            """,
            (emails,),
        )
        users = {row["email"]: row for row in cursor.fetchall()}
        cursor.execute(
            """
            SELECT u.email, ar.permission_scope, sp.code AS subportfolio_code,
                   p.code AS project_code, ar.can_read, ar.can_write, ar.can_export
              FROM public.access_rules ar
              JOIN public.users u ON u.id = ar.user_id
              LEFT JOIN public.subportfolios sp ON sp.id = ar.subportfolio_id
              LEFT JOIN public.projects p ON p.id = ar.project_id
             WHERE u.email = ANY(%s) AND ar.role_name IS NULL
            """,
            (emails,),
        )
        rules = cursor.fetchall()
        cursor.execute(
            """
            SELECT
              EXISTS(SELECT 1 FROM public.subportfolios WHERE id = %s AND partner_source_id = %s) AS demo_subportfolio,
              EXISTS(SELECT 1 FROM public.projects WHERE id = %s AND partner_source_id = %s AND subportfolio_id = %s) AS demo_project
            """,
            (
                DEMO_SUBPORTFOLIO_ID,
                DEMO_SUBPORTFOLIO_SOURCE_ID,
                DEMO_PROJECT_ID,
                DEMO_PROJECT_SOURCE_ID,
                DEMO_SUBPORTFOLIO_ID,
            ),
        )
        demo = cursor.fetchone()
        return {
            "auth_users": sum(user is not None for user in auth_users.values()),
            "public_users": len(users),
            "access_rules": len(rules),
            "demo_subportfolio": demo["demo_subportfolio"],
            "demo_project": demo["demo_project"],
            "reference_targets": len(reference_ids),
        }


def resolve_auth_users(
    auth_admin: AuthAdmin, *, create: bool
) -> tuple[dict[str, dict | None], dict[str, int]]:
    resolved: dict[str, dict | None] = {}
    counts = {"existing": 0, "created": 0, "would_create": 0}
    shared_password = os.getenv("MVP_AUTH_PASSWORD", "")
    for spec in IDENTITIES:
        user = auth_admin.find_user_by_email(spec.email)
        if user is not None:
            resolved[spec.key] = user
            counts["existing"] += 1
            continue
        if not create:
            resolved[spec.key] = None
            counts["would_create"] += 1
            continue
        password = os.getenv(spec.password_env, "") or shared_password
        if not password:
            raise RuntimeError(
                f"Defina {spec.password_env} ou MVP_AUTH_PASSWORD no ambiente."
            )
        resolved[spec.key] = auth_admin.create_user(spec.email, password)
        counts["created"] += 1
    return resolved, counts


def run_seed(auth_admin: AuthAdmin, repository: AccessRepository, *, dry_run: bool) -> dict:
    auth_users, auth_counts = resolve_auth_users(auth_admin, create=not dry_run)
    if dry_run:
        database = repository.inspect(auth_users)
    else:
        if any(user is None for user in auth_users.values()):
            raise RuntimeError("Nao foi possivel resolver todas as identidades Auth.")
        database = repository.upsert_all(auth_users)  # type: ignore[arg-type]
    return {"mode": "dry-run" if dry_run else "apply", "auth": auth_counts, "database": database}


def _load_environment() -> None:
    script_path = Path(__file__).resolve()
    load_dotenv(script_path.parents[1] / ".env", override=False)
    load_dotenv(script_path.parents[3] / ".env", override=False)


def _required_environment() -> tuple[str, str, str]:
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    database_url = (
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("SUPABASE_DATABASE_URL", "").strip()
    )
    missing = [
        name
        for name, value in (
            ("SUPABASE_URL", supabase_url),
            ("SUPABASE_SERVICE_ROLE_KEY", service_key),
            ("DATABASE_URL/SUPABASE_DATABASE_URL", database_url),
        )
        if not value
    ]
    if missing:
        raise RuntimeError("Variaveis obrigatorias ausentes: " + ", ".join(missing))
    expected_host = f"{EXPECTED_PROJECT_ID}.supabase.co"
    if expected_host not in supabase_url:
        raise RuntimeError(
            "SUPABASE_URL nao corresponde ao projeto Oneshot esperado "
            f"({EXPECTED_PROJECT_ID})."
        )
    return supabase_url, service_key, database_url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspeciona Auth e banco sem criar ou atualizar registros.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _load_environment()
    supabase_url, service_key, database_url = _required_environment()
    auth_admin = SupabaseAuthAdmin(supabase_url, service_key)
    try:
        result = run_seed(
            auth_admin,
            PostgresAccessRepository(database_url),
            dry_run=args.dry_run,
        )
    finally:
        auth_admin.close()
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
