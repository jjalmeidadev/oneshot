"""Processos independentes do scheduler e consumidores RabbitMQ."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import date
from typing import Any

from dotenv import load_dotenv

from app.alerts.messaging import Message, RabbitMQBroker
from app.alerts.repository import get_alert_repository
from app.alerts.schemas import AlertNotification
from app.alerts.service import get_alert_service
from app.database.connection import open_database_connection


async def run_evaluator() -> None:
    broker=RabbitMQBroker()
    async def handle(message: Message) -> None:
        get_alert_service().evaluate(
            message.payload["subscription_id"],
            date.fromisoformat(message.payload["as_of"]),
            evaluation_id=message.event_id,
        )
    try: await broker.consume("alert.evaluation.requested",handle)
    finally: await broker.close()


async def run_notifier() -> None:
    broker = RabbitMQBroker()

    async def handle(message: Message) -> None:
        notification = AlertNotification.model_validate(message.payload["notification"])
        get_alert_repository().create_notification(
            notification,
            str(message.payload["episode_key"]),
        )

    try:
        await broker.consume("alert.notification.requested", handle)
    finally:
        await broker.close()


def _claim_outbox(limit: int = 100) -> list[dict[str, Any]]:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH claimed AS (
                    SELECT event_id FROM public.message_outbox
                    WHERE status = 'pending' AND available_at <= NOW()
                    ORDER BY created_at
                    FOR UPDATE SKIP LOCKED LIMIT %s
                )
                UPDATE public.message_outbox AS item
                SET status='publishing', attempts=attempts+1, last_error=NULL
                FROM claimed WHERE item.event_id=claimed.event_id
                RETURNING item.event_id::text,item.event_type,item.correlation_id,item.payload;
                """,
                (limit,),
            )
            values = [
                {
                    "event_id": row[0],
                    "event_type": row[1],
                    "correlation_id": row[2],
                    "payload": row[3],
                }
                for row in cursor.fetchall()
            ]
        connection.commit()
        return values
    finally:
        connection.close()


def _finish_outbox(event_id: str, error: str | None = None) -> None:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            if error is None:
                cursor.execute(
                    "UPDATE public.message_outbox SET status='published',published_at=NOW() WHERE event_id=%s::uuid",
                    (event_id,),
                )
            else:
                cursor.execute(
                    """
                    UPDATE public.message_outbox
                    SET status=CASE WHEN attempts>=5 THEN 'failed' ELSE 'pending' END,
                        available_at=NOW() + (LEAST(attempts,5) * INTERVAL '30 seconds'),
                        last_error=%s
                    WHERE event_id=%s::uuid
                    """,
                    (error[:1000], event_id),
                )
        connection.commit()
    finally:
        connection.close()


async def publish_outbox_once() -> int:
    broker = RabbitMQBroker()
    count = 0
    try:
        for raw in _claim_outbox():
            try:
                await broker.publish(Message(**raw))
                _finish_outbox(raw["event_id"])
                count += 1
            except Exception as error:
                _finish_outbox(raw["event_id"], str(error))
    finally:
        await broker.close()
    return count


async def run_scheduler() -> None:
    interval = max(int(os.getenv("ALERT_SCHEDULER_INTERVAL_SECONDS", "60")), 5)
    while True:
        get_alert_service().schedule_due()
        await asyncio.sleep(interval)


async def run_publisher() -> None:
    interval = max(float(os.getenv("ALERT_OUTBOX_POLL_SECONDS", "2")), 0.25)
    while True:
        published = await publish_outbox_once()
        if published == 0:
            await asyncio.sleep(interval)


def main() -> int:
    load_dotenv()
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=["schedule-once","scheduler","publisher-once","publisher","evaluator","notifier"]); args=parser.parse_args()
    if args.command=="schedule-once": get_alert_service().schedule_due(); return 0
    if args.command=="scheduler": asyncio.run(run_scheduler()); return 0
    if args.command=="publisher-once": print(json.dumps({"published":asyncio.run(publish_outbox_once())})); return 0
    if args.command=="publisher": asyncio.run(run_publisher()); return 0
    if args.command=="notifier": asyncio.run(run_notifier()); return 0
    asyncio.run(run_evaluator()); return 0


if __name__=="__main__": raise SystemExit(main())
