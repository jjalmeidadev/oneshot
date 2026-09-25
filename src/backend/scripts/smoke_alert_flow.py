"""E2E controlado da API, outbox, RabbitMQ, worker e PostgreSQL."""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from dotenv import load_dotenv

from app.alerts.repository import get_alert_repository
from app.alerts.worker import publish_outbox_once
from app.database.connection import open_database_connection


def _evaluation_outcome(event_id: str) -> str | None:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT outcome FROM public.alert_evaluations WHERE evaluation_id=%s::uuid",
                (event_id,),
            )
            row = cursor.fetchone()
            return str(row[0]) if row else None
    finally:
        connection.close()


def _eligible_project_id() -> str:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT project_id::text
                FROM public.schedule_items
                WHERE planned_end_date < CURRENT_DATE
                  AND actual_end_date IS NULL
                  AND progress_percent < 100
                  AND status NOT IN ('concluido','cancelado')
                  AND updated_at >= NOW() - INTERVAL '45 days'
                UNION
                SELECT project_id::text
                FROM public.project_deliverables_milestones
                WHERE planned_date < CURRENT_DATE
                  AND completed_date IS NULL
                  AND COALESCE(status,'') NOT IN ('concluido','cancelado')
                  AND updated_at >= NOW() - INTERVAL '45 days'
                LIMIT 1;
                """
            )
            row = cursor.fetchone()
            if not row:
                raise RuntimeError(
                    "Nao existe item vencido, aberto e atualizado para o smoke elegivel."
                )
            return str(row[0])
    finally:
        connection.close()


def run(token: str, base_url: str, mode: str) -> None:
    load_dotenv()
    headers = {"Authorization": f"Bearer {token}"}
    subscription: dict | None = None
    with httpx.Client(base_url=base_url, headers=headers, timeout=20) as client:
        workflow = client.post(
            "/api/alert-workflow-sessions",
            json={
                "contract_version": "1.0",
                "conversation_id": f"smoke-{uuid4()}",
                "parameters": {},
            },
        )
        workflow.raise_for_status()
        state = workflow.json()
        options = state["question"]["options"]
        if not options:
            raise RuntimeError("Nenhum projeto disponivel para o smoke test.")
        project_id = (
            _eligible_project_id() if mode == "eligible" else options[0]["value"]
        )
        if project_id not in {option["value"] for option in options}:
            raise RuntimeError("Projeto elegivel nao foi oferecido pelo contrato da API.")
        answers = (
            ("project", project_id),
            ("threshold", 0 if mode == "eligible" else 3650),
            ("schedule", "daily"),
            ("resend", "none"),
        )
        for index, (step, value) in enumerate(answers):
            response = client.post(
                f"/api/alert-workflow-sessions/{state['session_id']}/answers",
                json={
                    "step": step,
                    "value": value,
                    "revision": state["revision"],
                    "client_action_id": f"smoke-answer-{index}-{uuid4()}",
                },
            )
            response.raise_for_status()
            state = response.json()
        confirmed = client.post(
            f"/api/alert-workflow-sessions/{state['session_id']}/confirm",
            json={
                "revision": state["revision"],
                "client_action_id": f"smoke-confirm-{uuid4()}",
            },
        )
        confirmed.raise_for_status()
        subscription = confirmed.json()["subscription"]
        event_id = str(uuid4())
        get_alert_repository().enqueue(
            event_id,
            "alert.evaluation.requested",
            subscription["correlation_id"],
            {
                "subscription_id": subscription["subscription_id"],
                "as_of": datetime.now(timezone.utc).date().isoformat(),
            },
        )
        asyncio.run(publish_outbox_once())
        outcome = None
        for _ in range(20):
            outcome = _evaluation_outcome(event_id)
            if outcome:
                break
            time.sleep(0.5)
        expected_outcome = "matched" if mode == "eligible" else "not_matched"
        if outcome != expected_outcome:
            raise RuntimeError(f"Resultado inesperado da avaliacao: {outcome}")
        notification_status = "not_applicable"
        if mode == "eligible":
            asyncio.run(publish_outbox_once())
            notification = None
            for _ in range(20):
                response = client.get("/api/notifications")
                response.raise_for_status()
                notification = next(
                    (
                        item
                        for item in response.json()["items"]
                        if item["subscription_id"] == subscription["subscription_id"]
                    ),
                    None,
                )
                if notification:
                    break
                time.sleep(0.5)
            if notification is None:
                raise RuntimeError("A notificacao elegivel nao foi persistida.")
            marked = client.post(
                f"/api/notifications/{notification['notification_id']}/read"
            )
            marked.raise_for_status()
            notification_status = marked.json()["status"]
        cancelled = client.post(
            f"/api/alert-subscriptions/{subscription['subscription_id']}/cancel",
            json={
                "revision": subscription["revision"],
                "client_action_id": f"smoke-cancel-{uuid4()}",
            },
        )
        cancelled.raise_for_status()
        print("ALERT_E2E=ok")
        print(f"EVALUATION_OUTCOME={outcome}")
        print(f"NOTIFICATION_STATUS={notification_status}")
        print(f"SUBSCRIPTION_STATUS={cancelled.json()['subscription']['status']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.getenv("ALERT_SMOKE_TOKEN"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--mode", choices=("eligible", "not-eligible"), default="not-eligible"
    )
    args = parser.parse_args()
    if not args.token:
        parser.error("Informe --token ou ALERT_SMOKE_TOKEN.")
    run(args.token, args.base_url, args.mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
