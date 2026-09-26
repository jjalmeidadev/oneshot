"""Aplica e verifica o isolamento das tabelas internas de relatorios."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from app.database.connection import open_database_connection


LOCK_NAME = "g05:guided-report-infrastructure"
SQL_DIR = Path(__file__).resolve().parents[2] / "database" / "sql"
MIGRATION = SQL_DIR / "11_secure_report_workflow_tables.sql"
ROLLBACK = SQL_DIR / "12_rollback_secure_report_workflow_tables.sql"
TABLES = (
    "report_executions",
    "generated_reports",
    "automation_callbacks",
    "workflow_sessions",
    "workflow_answers",
)


def _body(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if lines and lines[0].strip().upper() == "BEGIN;":
        lines = lines[1:]
    if lines and lines[-1].strip().upper() == "COMMIT;":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _state(cursor: object) -> tuple[int, bool, bool, bool]:
    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(BOOL_AND(c.relrowsecurity), FALSE),
            COALESCE(BOOL_OR(
                has_table_privilege('anon', c.oid, 'SELECT')
            ), FALSE),
            COALESCE(BOOL_OR(
                has_table_privilege('authenticated', c.oid, 'SELECT')
            ), FALSE)
        FROM pg_class AS c
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname = ANY(%s)
        """,
        (list(TABLES),),
    )
    return cursor.fetchone()


def run(mode: str) -> None:
    load_dotenv()
    connection = open_database_connection()
    locked = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_try_advisory_lock(hashtext(%s))", (LOCK_NAME,)
            )
            locked = bool(cursor.fetchone()[0])
            if not locked:
                raise RuntimeError("Outra migracao de relatorios esta em andamento.")
            connection.commit()

            if mode == "verify":
                state = _state(cursor)
                connection.rollback()
            else:
                cursor.execute("BEGIN")
                cursor.execute(_body(ROLLBACK if mode == "rollback-dry-run" else MIGRATION))
                state = _state(cursor)
                if mode == "rollback-dry-run":
                    expected = state == (5, False, False, False)
                else:
                    expected = state == (5, True, False, False)
                if not expected:
                    raise RuntimeError("Estado de seguranca inesperado.")
                if mode in {"dry-run", "rollback-dry-run"}:
                    connection.rollback()
                else:
                    connection.commit()

            count, rls, anon_select, authenticated_select = state
            print(f"MODE={mode}")
            print(f"TABLE_COUNT={count}")
            print(f"RLS_ALL={rls}")
            print(f"ANON_SELECT_ANY={anon_select}")
            print(f"AUTH_SELECT_ANY={authenticated_select}")
    except Exception:
        connection.rollback()
        raise
    finally:
        if locked:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_advisory_unlock(hashtext(%s))", (LOCK_NAME,)
                )
            connection.commit()
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", choices=("dry-run", "apply", "verify", "rollback-dry-run")
    )
    run(parser.parse_args().mode)


if __name__ == "__main__":
    main()
