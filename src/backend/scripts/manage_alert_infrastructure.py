"""Inspeciona e aplica migrações PostgreSQL de alertas em etapas explícitas."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from app.database.connection import open_database_connection

ROOT = Path(__file__).resolve().parents[3]
PREPARE = ROOT / "src" / "database" / "sql" / "08_add_prepared_proactive_response.sql"
APPLY = ROOT / "src" / "database" / "sql" / "15_alert_deadline_flow.sql"
ROLLBACK = ROOT / "src" / "database" / "sql" / "16_rollback_alert_deadline_flow.sql"
ALERT_TABLES = (
    "alert_subscriptions",
    "alert_evaluations",
    "alert_occurrences",
    "alert_notifications",
    "notification_delivery_attempts",
    "message_outbox",
)


def execute(path: Path) -> None:
    load_dotenv()
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(path.read_text(encoding="utf-8"))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def schema_status() -> dict[str, bool]:
    load_dotenv()
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.relrowsecurity,
                       (SELECT count(*) = 2 FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = 'pending_proactive_suggestions'
                          AND column_name IN ('prepared_response', 'prepared_model')
                          AND is_nullable = 'NO'),
                       EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_schema = 'public'
                                 AND table_name = 'pending_proactive_suggestions'
                                 AND column_name = 'prepared_interaction_id'
                                 AND is_nullable = 'YES'),
                       NOT has_table_privilege('anon', c.oid, 'SELECT,INSERT,UPDATE,DELETE'),
                       NOT has_table_privilege('authenticated', c.oid, 'SELECT,INSERT,UPDATE,DELETE')
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relname = 'pending_proactive_suggestions';
                """
            )
            prepared = cursor.fetchone()
            cursor.execute(
                "SELECT to_regclass('public.' || name) IS NOT NULL "
                "FROM unnest(%s::text[]) AS name",
                (list(ALERT_TABLES),),
            )
            present = [row[0] for row in cursor.fetchall()]
        return {
            "migration_08_ready": bool(prepared and all(prepared)),
            **dict(zip(ALERT_TABLES, present, strict=True)),
        }
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare-proactive", "apply", "status", "rollback"])
    parser.add_argument("--confirm-expired-cleanup", action="store_true")
    parser.add_argument("--confirm-destructive", action="store_true")
    args = parser.parse_args()
    if args.command == "status":
        print(schema_status())
    elif args.command == "prepare-proactive":
        if not args.confirm_expired_cleanup:
            parser.error("A migração 08 pode remover legados expirados; use --confirm-expired-cleanup.")
        execute(PREPARE)
    elif args.command == "apply":
        current = schema_status()
        if not current["migration_08_ready"]:
            parser.error("A migração 08 deve estar concluída antes da 15 e do novo runtime.")
        if any(current[name] for name in ALERT_TABLES):
            parser.error("Tabelas de alertas já existem; não reaplique 15. Verifique compatibilidade em leitura.")
        execute(APPLY)
    else:
        if not args.confirm_destructive:
            parser.error("O rollback 16 exclui tabelas e dados; use --confirm-destructive.")
        execute(ROLLBACK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
