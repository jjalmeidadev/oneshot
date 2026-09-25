"""Aplica, inspeciona ou reverte a infraestrutura PostgreSQL de alertas."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from app.database.connection import open_database_connection

ROOT = Path(__file__).resolve().parents[3]
APPLY = ROOT / "src" / "database" / "sql" / "15_alert_deadline_flow.sql"
ROLLBACK = ROOT / "src" / "database" / "sql" / "16_rollback_alert_deadline_flow.sql"


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


def status() -> None:
    load_dotenv()
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT to_regclass('public.alert_subscriptions') IS NOT NULL,
                       to_regclass('public.alert_evaluations') IS NOT NULL,
                       to_regclass('public.alert_notifications') IS NOT NULL,
                       to_regclass('public.message_outbox') IS NOT NULL;
                """
            )
            subscriptions, evaluations, notifications, outbox = cursor.fetchone()
        print(
            {
                "alert_subscriptions": subscriptions,
                "alert_evaluations": evaluations,
                "alert_notifications": notifications,
                "message_outbox": outbox,
            }
        )
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["apply", "status", "rollback"])
    args = parser.parse_args()
    if args.command == "status":
        status()
    else:
        execute(APPLY if args.command == "apply" else ROLLBACK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
