"""Dry-run, aplicacao e verificacao da infraestrutura de relatorios."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from app.database.connection import open_database_connection


LOCK_NAME = "g05:guided-report-infrastructure"
SQL_DIR = Path(__file__).resolve().parents[2] / "database" / "sql"
MIGRATIONS = (
    SQL_DIR / "05_report_generation.sql",
    SQL_DIR / "07_guided_report_workflow.sql",
    SQL_DIR / "09_create_report_storage_bucket.sql",
)
ROLLBACKS = (
    SQL_DIR / "08_rollback_guided_report_workflow.sql",
    SQL_DIR / "06_rollback_report_generation.sql",
)


def _migration_body(path: Path) -> str:
    sql = path.read_text(encoding="utf-8").strip()
    lines = sql.splitlines()
    if lines and lines[0].strip().upper() == "BEGIN;":
        lines = lines[1:]
    if lines and lines[-1].strip().upper() == "COMMIT;":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _verify(cursor: object) -> tuple[bool, bool, bool, bool]:
    cursor.execute(
        """
        SELECT
            to_regclass('public.workflow_sessions') IS NOT NULL,
            to_regclass('public.workflow_answers') IS NOT NULL,
            EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'report_executions'
                  AND column_name = 'snapshot_payload'
            ),
            EXISTS (
                SELECT 1
                FROM storage.buckets
                WHERE id = 'generated-reports'
                  AND public IS FALSE
                  AND file_size_limit = 10485760
                  AND allowed_mime_types = ARRAY[
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                  ]::TEXT[]
            )
        """
    )
    return cursor.fetchone()


def _should_apply(cursor: object, migration: Path) -> bool:
    """Evita reaplicar DDL e denuncia estados parciais em vez de mascara-los."""
    if migration.name == "05_report_generation.sql":
        cursor.execute(
            """
            SELECT COUNT(*) FROM unnest(ARRAY[
                to_regclass('public.report_executions'),
                to_regclass('public.generated_reports'),
                to_regclass('public.automation_callbacks')
            ]) AS object_name WHERE object_name IS NOT NULL
            """
        )
        count = int(cursor.fetchone()[0])
        if count not in {0, 3}:
            raise RuntimeError("Migracao 05 esta parcialmente aplicada; abortando.")
        return count == 0
    if migration.name == "07_guided_report_workflow.sql":
        cursor.execute(
            """
            SELECT
                (to_regclass('public.workflow_sessions') IS NOT NULL)::int
              + (to_regclass('public.workflow_answers') IS NOT NULL)::int
              + (EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='report_executions'
                      AND column_name='snapshot_payload'
                ))::int
            """
        )
        count = int(cursor.fetchone()[0])
        if count not in {0, 3}:
            raise RuntimeError("Migracao 07 esta parcialmente aplicada; abortando.")
        return count == 0
    if migration.name == "09_create_report_storage_bucket.sql":
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM storage.buckets
                WHERE id='generated-reports' AND public IS FALSE
                  AND file_size_limit=10485760
                  AND allowed_mime_types=ARRAY[
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                  ]::TEXT[]
            )
            """
        )
        return not bool(cursor.fetchone()[0])
    return True


def run(mode: str) -> None:
    load_dotenv()
    connection = open_database_connection()
    lock_acquired = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_try_advisory_lock(hashtext(%s))", (LOCK_NAME,)
            )
            lock_acquired = bool(cursor.fetchone()[0])
            if not lock_acquired:
                raise RuntimeError("Outra migracao de relatorios esta em andamento.")
            connection.commit()

            if mode == "verify":
                state = _verify(cursor)
                connection.rollback()
            else:
                cursor.execute("BEGIN")
                scripts = ROLLBACKS if mode == "rollback-dry-run" else MIGRATIONS
                for migration in scripts:
                    if mode == "rollback-dry-run" or _should_apply(cursor, migration):
                        cursor.execute(_migration_body(migration))
                state = _verify(cursor)
                expected = (
                    state == (False, False, False, True)
                    if mode == "rollback-dry-run"
                    else all(state)
                )
                if not expected:
                    raise RuntimeError("A verificacao pos-migracao nao foi satisfeita.")
                if mode in {"dry-run", "rollback-dry-run"}:
                    connection.rollback()
                else:
                    connection.commit()

            labels = (
                "workflow_sessions",
                "workflow_answers",
                "snapshot_payload",
                "private_bucket",
            )
            print(f"MODE={mode}")
            for label, enabled in zip(labels, state, strict=True):
                print(f"{label.upper()}={enabled}")
    except Exception:
        connection.rollback()
        raise
    finally:
        if lock_acquired:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_advisory_unlock(hashtext(%s))", (LOCK_NAME,)
                )
            connection.commit()
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("dry-run", "apply", "verify", "rollback-dry-run"),
    )
    arguments = parser.parse_args()
    run(arguments.mode)


if __name__ == "__main__":
    main()
