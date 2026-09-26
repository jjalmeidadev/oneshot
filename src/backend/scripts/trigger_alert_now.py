"""Antecipa a avaliacao de uma inscricao ativa para disparo imediato.

Uso em teste manual: apos criar um alerta pelo chat, este utilitario coloca
`next_evaluation_at` no passado e enfileira `alert.evaluation.requested` na
outbox (na mesma transacao), de modo que o publisher/evaluator/notifier
processem a inscricao em segundos pela cadeia real (outbox -> RabbitMQ -> banco).

Exemplos:
    python -m scripts.trigger_alert_now                 # inscricao ativa mais recente
    python -m scripts.trigger_alert_now --subscription-id <uuid>
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv

from app.database.connection import open_database_connection


def _latest_active_subscription() -> tuple[str, str] | None:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT subscription_id::text, correlation_id
                FROM public.alert_subscriptions
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT 1;
                """
            )
            row = cursor.fetchone()
            return (str(row[0]), str(row[1])) if row else None
    finally:
        connection.close()


def _correlation_of(subscription_id: str) -> str | None:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT correlation_id FROM public.alert_subscriptions WHERE subscription_id=%s::uuid AND status='active'",
                (subscription_id,),
            )
            row = cursor.fetchone()
            return str(row[0]) if row else None
    finally:
        connection.close()


def trigger(subscription_id: str, correlation_id: str) -> str:
    event_id = str(uuid4())
    now = datetime.now(timezone.utc)
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            # Antecipa a proxima avaliacao (o scheduler tambem a pegaria no proximo ciclo).
            cursor.execute(
                "UPDATE public.alert_subscriptions SET next_evaluation_at=%s WHERE subscription_id=%s::uuid",
                (now, subscription_id),
            )
            # Enfileira a avaliacao imediata na outbox (mesma transacao).
            cursor.execute(
                """
                INSERT INTO public.message_outbox (event_id,event_type,correlation_id,payload)
                VALUES (%s::uuid,'alert.evaluation.requested',%s,%s::jsonb)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (
                    event_id,
                    correlation_id,
                    json.dumps(
                        {
                            "subscription_id": subscription_id,
                            "as_of": now.date().isoformat(),
                        }
                    ),
                ),
            )
        connection.commit()
        return event_id
    finally:
        connection.close()


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--subscription-id")
    args = parser.parse_args()

    if args.subscription_id:
        correlation = _correlation_of(args.subscription_id)
        if not correlation:
            print("SUBSCRIPTION_NOT_FOUND_OR_INACTIVE")
            return 1
        target = (args.subscription_id, correlation)
    else:
        target = _latest_active_subscription()
        if not target:
            print("NO_ACTIVE_SUBSCRIPTION")
            return 1

    event_id = trigger(*target)
    print(f"TRIGGERED_SUBSCRIPTION={target[0]}")
    print(f"EVENT_ID={event_id}")
    print("Aguarde alguns segundos e confira a central de notificacoes no chat.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
