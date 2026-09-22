"""Leitura deterministica da massa sintetica usada pelo simulador local."""

from __future__ import annotations

import json
import hashlib
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from app.reports.errors import ReportError
from app.reports.schemas import PreparedReport, ScopeType

DEFAULT_DATA_PATH = Path(__file__).with_name("data") / "synthetic_portfolio.json"


class SyntheticPortfolioSource:
    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or DEFAULT_DATA_PATH

    def scope_metadata(self, scope_type: ScopeType, scope_id: str) -> dict[str, Any]:
        data = self._load()
        collection = (
            data["projects"]
            if scope_type == ScopeType.PROJECT
            else data["subportfolios"]
        )
        for item in collection:
            if scope_id in {item["id"], item.get("code")}:
                return {
                    "id": item["id"],
                    "code": item.get("code"),
                    "title": item["title"],
                    "updated_at": item["updated_at"],
                }
        raise ReportError(
            "REPORT_SCOPE_NOT_FOUND",
            "O projeto ou subportfolio informado nao foi encontrado.",
            404,
        )

    def list_scopes(self, scope_type: ScopeType) -> list[dict[str, Any]]:
        """Lista apenas escopos da massa controlada; a autorizacao filtra o retorno."""

        data = self._load()
        collection = (
            data["projects"]
            if scope_type == ScopeType.PROJECT
            else data["subportfolios"]
        )
        return [
            {
                "id": item["id"],
                "code": item.get("code"),
                "title": item["title"],
                "updated_at": item["updated_at"],
            }
            for item in collection
        ]

    def build_snapshot(self, prepared: PreparedReport) -> dict[str, Any]:
        data = self._load()
        if prepared.scope.type == ScopeType.PROJECT:
            projects = [
                item
                for item in data["projects"]
                if prepared.scope.id in {item["id"], item.get("code")}
            ]
            subportfolio = next(
                (
                    item
                    for item in data["subportfolios"]
                    if projects and item["id"] == projects[0]["subportfolio_id"]
                ),
                None,
            )
        else:
            subportfolio = next(
                (
                    item
                    for item in data["subportfolios"]
                    if prepared.scope.id in {item["id"], item.get("code")}
                ),
                None,
            )
            projects = [
                item
                for item in data["projects"]
                if subportfolio and item["subportfolio_id"] == subportfolio["id"]
            ]
        if not projects or subportfolio is None:
            raise ReportError(
                "REPORT_DATA_UNAVAILABLE",
                "Nao ha dados suficientes para gerar o relatorio solicitado.",
                422,
            )

        project_ids = {item["id"] for item in projects}
        snapshot = {
            "contract_version": prepared.contract_version,
            "scope": prepared.scope.model_dump(mode="json"),
            "scope_title": prepared.scope_title,
            "period": prepared.period.model_dump(mode="json"),
            "subportfolio": deepcopy(subportfolio),
            "projects": deepcopy(projects),
            "risks": self._filter(data["risks"], project_ids),
            "milestones": self._filter(data["milestones"], project_ids),
            "benefits": self._filter(data["benefits"], project_ids),
            "changes": self._filter(data["changes"], project_ids),
            "sources": [
                {
                    **deepcopy(item),
                    "source_id": _source_id(item),
                }
                for item in data["sources"]
            ],
            "limitations": list(data.get("limitations", [])),
            "captured_at": datetime.now().astimezone().isoformat(),
        }
        return snapshot

    @staticmethod
    def _filter(
        items: list[dict[str, Any]], project_ids: set[str]
    ) -> list[dict[str, Any]]:
        return [deepcopy(item) for item in items if item["project_id"] in project_ids]

    def _load(self) -> dict[str, Any]:
        try:
            return json.loads(self.data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, KeyError) as error:
            raise ReportError(
                "REPORT_SOURCE_UNAVAILABLE",
                "A fonte de dados do relatorio esta indisponivel.",
                503,
            ) from error


def _source_id(source: dict[str, Any]) -> str:
    canonical = f"{source.get('source_type', '')}:{source.get('locator', '')}"
    return f"src-{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:12]}"



# Limitacoes aplicaveis quando a fonte e o banco real (nao a massa sintetica).
_DATABASE_LIMITATIONS = [
    "Relatorio gerado a partir da base de portfolio do banco de dados.",
    "Valores financeiros e beneficios realizados dependem da carga disponivel no periodo.",
    "A integracao com Power Automate, AI Builder e identidade corporativa depende de provisionamento externo.",
]


class PostgresPortfolioSource:
    """Fonte de portfolio que le das tabelas reais do PostgreSQL/Supabase.

    Produz exatamente o mesmo formato de snapshot que ``SyntheticPortfolioSource``
    para ser intercambiavel na interface consumida por ``ReportService``. O
    identificador publico de escopo e o ``code`` (ex.: ``PRJ-0442``), ja que o
    ``id`` fisico das tabelas e um UUID.
    """

    def __init__(self, connection_factory: Any | None = None) -> None:
        self._connection_factory = connection_factory

    # -- infraestrutura -----------------------------------------------------
    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        from app.database.connection import open_database_connection

        return open_database_connection()

    @staticmethod
    def _cursor(conn: Any) -> Any:
        try:
            from psycopg.rows import dict_row

            return conn.cursor(row_factory=dict_row)
        except Exception:
            # Fallback para conexoes que nao suportam row_factory (ex.: duplos de teste).
            return conn.cursor()

    # -- interface publica --------------------------------------------------
    def scope_metadata(self, scope_type: ScopeType, scope_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            cur = self._cursor(conn)
            table = "projects" if scope_type == ScopeType.PROJECT else "subportfolios"
            cur.execute(
                f"select id, code, title, updated_at from public.{table} "
                "where code = %s or id::text = %s limit 1",
                (scope_id, scope_id),
            )
            row = cur.fetchone()
            if not row:
                raise ReportError(
                    "REPORT_SCOPE_NOT_FOUND",
                    "O projeto ou subportfolio informado nao foi encontrado.",
                    404,
                )
            return {
                "id": row["code"] or str(row["id"]),
                "code": row["code"],
                "title": row["title"],
                "updated_at": _iso(row["updated_at"]),
            }
        finally:
            self._close(conn)

    def list_scopes(self, scope_type: ScopeType) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            cur = self._cursor(conn)
            table = "projects" if scope_type == ScopeType.PROJECT else "subportfolios"
            cur.execute(
                f"select id, code, title, updated_at from public.{table} "
                "order by code"
            )
            return [
                {
                    "id": row["code"] or str(row["id"]),
                    "code": row["code"],
                    "title": row["title"],
                    "updated_at": _iso(row["updated_at"]),
                }
                for row in cur.fetchall()
            ]
        finally:
            self._close(conn)

    def build_snapshot(self, prepared: PreparedReport) -> dict[str, Any]:
        conn = self._connect()
        try:
            cur = self._cursor(conn)
            if prepared.scope.type == ScopeType.PROJECT:
                cur.execute(
                    "select * from public.projects where code = %s or id::text = %s",
                    (prepared.scope.id, prepared.scope.id),
                )
                projects = cur.fetchall()
                subportfolio = None
                if projects:
                    cur.execute(
                        "select * from public.subportfolios where id = %s",
                        (projects[0]["subportfolio_id"],),
                    )
                    subportfolio = cur.fetchone()
            else:
                cur.execute(
                    "select * from public.subportfolios where code = %s or id::text = %s",
                    (prepared.scope.id, prepared.scope.id),
                )
                subportfolio = cur.fetchone()
                projects = []
                if subportfolio:
                    cur.execute(
                        "select * from public.projects where subportfolio_id = %s "
                        "order by code",
                        (subportfolio["id"],),
                    )
                    projects = cur.fetchall()

            if not projects or subportfolio is None:
                raise ReportError(
                    "REPORT_DATA_UNAVAILABLE",
                    "Nao ha dados suficientes para gerar o relatorio solicitado.",
                    422,
                )

            project_uuids = [row["id"] for row in projects]
            snapshot = {
                "contract_version": prepared.contract_version,
                "scope": prepared.scope.model_dump(mode="json"),
                "scope_title": prepared.scope_title,
                "period": prepared.period.model_dump(mode="json"),
                "subportfolio": self._subportfolio(subportfolio),
                "projects": [
                    self._project(cur, row) for row in projects
                ],
                "risks": self._risks(cur, project_uuids),
                "milestones": self._milestones(cur, project_uuids),
                "benefits": self._benefits(cur, project_uuids),
                "changes": self._changes(cur, project_uuids),
                "sources": self._sources(cur, project_uuids),
                "limitations": list(_DATABASE_LIMITATIONS),
                "captured_at": datetime.now().astimezone().isoformat(),
            }
            return snapshot
        finally:
            self._close(conn)

    # -- montagem de blocos -------------------------------------------------
    @staticmethod
    def _subportfolio(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row.get("code") or str(row["id"]),
            "code": row.get("code"),
            "title": row.get("title"),
            "responsible": row.get("responsible_name") or "Gerencia de Portfolio",
            "strategic_objective": row.get("strategic_objective") or "",
            "updated_at": _iso(row.get("updated_at")),
        }

    def _project(self, cur: Any, row: dict[str, Any]) -> dict[str, Any]:
        planned, actual = self._latest_progress(cur, row["id"])
        achievements, next_steps = self._latest_status(cur, row["id"])
        return {
            "id": row.get("code") or str(row["id"]),
            "code": row.get("code"),
            "subportfolio_id": str(row.get("subportfolio_id")),
            "title": row.get("title"),
            "status": row.get("status") or "",
            "phase": row.get("current_phase") or "",
            "manager": row.get("project_manager_name") or "",
            "planned_progress": planned,
            "actual_progress": actual,
            "achievements": achievements,
            "next_steps": next_steps,
            "updated_at": _iso(row.get("updated_at")),
        }

    @staticmethod
    def _latest_progress(cur: Any, project_uuid: Any) -> tuple[float, float]:
        cur.execute(
            "select planned_physical, actual_physical from public.project_progress_updates "
            "where project_id = %s order by reference_date desc nulls last, created_at desc "
            "limit 1",
            (project_uuid,),
        )
        row = cur.fetchone()
        if not row:
            return 0.0, 0.0
        return (
            float(row["planned_physical"] or 0.0),
            float(row["actual_physical"] or 0.0),
        )

    @staticmethod
    def _latest_status(cur: Any, project_uuid: Any) -> tuple[str, str]:
        cur.execute(
            "select achievements, next_steps from public.project_status_updates "
            "where project_id = %s order by reference_date desc nulls last, created_at desc "
            "limit 1",
            (project_uuid,),
        )
        row = cur.fetchone()
        if not row:
            return "", ""
        return (row["achievements"] or "", row["next_steps"] or "")

    def _risks(self, cur: Any, project_uuids: list[Any]) -> list[dict[str, Any]]:
        cur.execute(
            "select project_id, title, criticality, mitigation_plan, owner_name, status "
            "from public.risk_issue_items where project_id = any(%s) "
            "order by criticality, title",
            (project_uuids,),
        )
        return [
            {
                "project_id": self._code_for(cur, row["project_id"]),
                "title": row.get("title") or row.get("risk_or_issue_text") or "",
                "criticality": row.get("criticality") or "",
                "mitigation": row.get("mitigation_plan") or "",
                "owner": row.get("owner_name") or "",
                "status": row.get("status") or "",
            }
            for row in cur.fetchall()
        ]

    def _milestones(self, cur: Any, project_uuids: list[Any]) -> list[dict[str, Any]]:
        cur.execute(
            "select project_id, description, planned_date, status "
            "from public.project_deliverables_milestones where project_id = any(%s) "
            "order by planned_date nulls last",
            (project_uuids,),
        )
        return [
            {
                "project_id": self._code_for(cur, row["project_id"]),
                "description": row.get("description") or "",
                "planned_date": _iso_date(row.get("planned_date")),
                "status": row.get("status") or "",
            }
            for row in cur.fetchall()
        ]

    def _benefits(self, cur: Any, project_uuids: list[Any]) -> list[dict[str, Any]]:
        cur.execute(
            "select project_id, description, measurement_indicator, expected_value "
            "from public.project_benefits where project_id = any(%s) order by description",
            (project_uuids,),
        )
        return [
            {
                "project_id": self._code_for(cur, row["project_id"]),
                "description": row.get("description") or "",
                "indicator": row.get("measurement_indicator") or "",
                "expected_value": row.get("expected_value") or "",
                "capture_start": "",
            }
            for row in cur.fetchall()
        ]

    def _changes(self, cur: Any, project_uuids: list[Any]) -> list[dict[str, Any]]:
        cur.execute(
            "select project_id, title, status, impact_summary "
            "from public.change_records where project_id = any(%s) "
            "order by registration_date nulls last",
            (project_uuids,),
        )
        return [
            {
                "project_id": self._code_for(cur, row["project_id"]),
                "title": row.get("title") or "",
                "status": row.get("status") or "",
                "impact": row.get("impact_summary") or "",
            }
            for row in cur.fetchall()
        ]

    def _sources(self, cur: Any, project_uuids: list[Any]) -> list[dict[str, Any]]:
        cur.execute(
            "select distinct source_title, source_type, source_locator, updated_at "
            "from public.consulted_sources where project_id = any(%s) "
            "order by source_title limit 20",
            (project_uuids,),
        )
        rows = cur.fetchall()
        sources: list[dict[str, Any]] = []
        for row in rows:
            item = {
                "title": row.get("source_title") or "Fonte de portfolio",
                "source_type": row.get("source_type") or "banco_de_dados",
                "locator": row.get("source_locator") or "db://portfolio",
                "last_updated": _iso(row.get("updated_at")),
            }
            item["source_id"] = _source_id(item)
            sources.append(item)
        if not sources:
            base = {
                "title": "Base de portfolio (PostgreSQL)",
                "source_type": "banco_de_dados",
                "locator": "db://public/projects",
                "last_updated": datetime.now().astimezone().isoformat(),
            }
            base["source_id"] = _source_id(base)
            sources.append(base)
        return sources

    # -- utilitarios --------------------------------------------------------
    _code_cache: dict[Any, str]

    def _code_for(self, cur: Any, project_uuid: Any) -> str:
        cache = getattr(self, "_code_cache", None)
        if cache is None:
            cache = {}
            self._code_cache = cache
        if project_uuid in cache:
            return cache[project_uuid]
        cur.execute(
            "select code from public.projects where id = %s", (project_uuid,)
        )
        row = cur.fetchone()
        code = (row.get("code") if row else None) or str(project_uuid)
        cache[project_uuid] = code
        return code

    @staticmethod
    def _close(conn: Any) -> None:
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def _iso(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.astimezone().isoformat() if value.tzinfo else value.isoformat()
    return str(value)


def _iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.isoformat() if hasattr(value, "isoformat") else str(value)
