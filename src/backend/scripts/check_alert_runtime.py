"""Resumo operacional sem dados sensíveis do fluxo de alertas."""

from dotenv import load_dotenv

from app.database.connection import open_database_connection


def main() -> int:
    load_dotenv()
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM public.alert_subscriptions),
                    (SELECT COUNT(*) FROM public.alert_evaluations),
                    (SELECT COUNT(*) FROM public.alert_notifications),
                    (SELECT COUNT(*) FROM public.message_outbox WHERE status='pending'),
                    (SELECT outcome FROM public.alert_evaluations ORDER BY completed_at DESC LIMIT 1),
                    (SELECT status FROM public.alert_subscriptions ORDER BY created_at DESC LIMIT 1);
                """
            )
            row = cursor.fetchone()
        print(f"SUBSCRIPTIONS={row[0]}")
        print(f"EVALUATIONS={row[1]}")
        print(f"NOTIFICATIONS={row[2]}")
        print(f"OUTBOX_PENDING={row[3]}")
        print(f"LATEST_EVALUATION={row[4]}")
        print(f"LATEST_SUBSCRIPTION={row[5]}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
