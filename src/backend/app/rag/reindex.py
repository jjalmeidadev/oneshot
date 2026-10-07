"""Carga e validação reproduzíveis da base SharePoint simulada."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.database.connection import open_database_connection


EXPECTED_PROJECT_CODES = ("PRJ-0442", "PRJ-0510", "PRJ-0587")
DEFAULT_SEED_PATH = (
    Path(__file__).resolve().parents[3]
    / "database"
    / "sql"
    / "04_rag_synthetic_data.sql"
)

COVERAGE_QUERY = """
SELECT
    p.code,
    COUNT(DISTINCT a.id) AS artifact_count,
    COUNT(DISTINCT se.id) AS extract_count
FROM public.projects p
LEFT JOIN public.project_artifacts a
    ON a.project_id = p.id
   AND a.partner_source_id LIKE 'sharepoint-mock:%'
   AND a.metadata ->> 'mock' = 'true'
LEFT JOIN public.source_extracts se
    ON se.artifact_id = a.id
   AND se.project_id = p.id
   AND se.metadata ->> 'mock' = 'true'
WHERE p.code = ANY(%s::text[])
GROUP BY p.code
ORDER BY p.code
"""

DUPLICATE_EXTRACTS_QUERY = """
SELECT COUNT(*)
FROM (
    SELECT se.artifact_id, se.source_locator
    FROM public.source_extracts se
    JOIN public.project_artifacts a ON a.id = se.artifact_id
    WHERE a.partner_source_id LIKE 'sharepoint-mock:%'
      AND se.metadata ->> 'mock' = 'true'
    GROUP BY se.artifact_id, se.source_locator
    HAVING COUNT(*) > 1
) duplicates
"""


class SharePointMockCoverageError(RuntimeError):
    """Indica que a carga terminou sem a cobertura documental esperada."""


def apply_sharepoint_mock_seed(
    connection: Any,
    *,
    seed_path: Path = DEFAULT_SEED_PATH,
) -> None:
    """Aplica a carga transacional; em falha, desfaz a conexão recebida."""

    sql = seed_path.read_text(encoding="utf-8")
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def inspect_sharepoint_mock_coverage(connection: Any) -> dict[str, object]:
    """Retorna cobertura por projeto e rejeita ausência ou duplicação."""

    with connection.cursor() as cursor:
        cursor.execute(COVERAGE_QUERY, (list(EXPECTED_PROJECT_CODES),))
        rows = cursor.fetchall()
        cursor.execute(DUPLICATE_EXTRACTS_QUERY)
        duplicate_row = cursor.fetchone()

    coverage = [
        {
            "project_code": str(row[0]),
            "artifact_count": int(row[1]),
            "extract_count": int(row[2]),
        }
        for row in rows
    ]
    covered_codes = {
        item["project_code"]
        for item in coverage
        if item["artifact_count"] >= 1 and item["extract_count"] >= 1
    }
    missing = sorted(set(EXPECTED_PROJECT_CODES) - covered_codes)
    duplicate_groups = int(duplicate_row[0]) if duplicate_row else 0
    if missing or duplicate_groups:
        details = []
        if missing:
            details.append("projetos sem cobertura: " + ", ".join(missing))
        if duplicate_groups:
            details.append(f"grupos de extratos duplicados: {duplicate_groups}")
        raise SharePointMockCoverageError("; ".join(details))

    return {
        "projects": coverage,
        "duplicate_extract_groups": duplicate_groups,
        "valid": True,
    }


def reindex_sharepoint_mock(
    *,
    connect: Callable[..., Any] | None = None,
    seed_path: Path = DEFAULT_SEED_PATH,
) -> dict[str, object]:
    """Aplica a carga e valida seu estado final em uma única operação."""

    connection = open_database_connection(connect=connect)
    try:
        apply_sharepoint_mock_seed(connection, seed_path=seed_path)
        return inspect_sharepoint_mock_coverage(connection)
    finally:
        connection.close()


def sharepoint_mock_status(
    *,
    connect: Callable[..., Any] | None = None,
) -> dict[str, object]:
    """Valida a cobertura existente sem executar a carga."""

    connection = open_database_connection(connect=connect)
    try:
        return inspect_sharepoint_mock_coverage(connection)
    finally:
        connection.close()
