"""CLI primario para configurar e operar alertas sem interface grafica."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from uuid import uuid4

from dotenv import load_dotenv

from app.alerts.errors import AlertError
from app.alerts.schemas import AlertRule, CreateAlertRequest, PrepareAlertRequest
from app.alerts.service import get_alert_service
from app.reports.security import resolve_report_identity


def main(argv: list[str]|None=None) -> int:
    load_dotenv()
    parser=_parser(); args=parser.parse_args(argv)
    token=os.getenv("ALERT_CLI_TOKEN",os.getenv("REPORT_CLI_TOKEN","")).strip()
    if not token: parser.error("Configure ALERT_CLI_TOKEN no ambiente.")
    try:
        identity=resolve_report_identity(f"Bearer {token}"); service=get_alert_service()
        if args.command=="create":
            prepared=service.prepare(PrepareAlertRequest(conversation_id=f"cli-{uuid4()}",rule=AlertRule(project_id=args.project_id,project_label=args.project_label,threshold_days=args.threshold)),identity)
            value,_=service.create(CreateAlertRequest(prepared_alert=prepared.prepared_alert,confirmation_hash=prepared.confirmation_hash,idempotency_key=args.idempotency_key or f"cli:{prepared.confirmation_hash}"),identity)
            print(value.model_dump_json(indent=2))
        elif args.command=="evaluate": print(service.evaluate(args.subscription_id,date.fromisoformat(args.as_of) if args.as_of else None).model_dump_json(indent=2))
        elif args.command=="schedule": print(json.dumps({"scheduled":service.schedule_due()},indent=2))
        elif args.command=="list": print(json.dumps([item.model_dump(mode="json") for item in service.list(identity)],indent=2,default=str))
        return 0
    except (AlertError,ValueError) as error:
        print(json.dumps({"error":getattr(error,"message",str(error))},ensure_ascii=False),file=sys.stderr); return 1


def _parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(description="Configura e executa alertas internos de prazo."); sub=parser.add_subparsers(dest="command",required=True)
    create=sub.add_parser("create"); create.add_argument("--project-id",required=True); create.add_argument("--project-label",required=True); create.add_argument("--threshold",required=True,type=int); create.add_argument("--idempotency-key")
    evaluate=sub.add_parser("evaluate"); evaluate.add_argument("--subscription-id",required=True); evaluate.add_argument("--as-of")
    sub.add_parser("schedule"); sub.add_parser("list"); return parser


if __name__=="__main__": raise SystemExit(main())
