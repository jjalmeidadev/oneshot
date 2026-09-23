"""CLI do simulador de relatorio, fonte primaria para operacao local."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from uuid import uuid4

from app.reports.errors import ReportError
from app.reports.schemas import (
    Audience,
    CreateReportRequest,
    Emphasis,
    PrepareReportRequest,
    Purpose,
    ReportOptions,
    ReportPeriod,
    ReportScope,
    ScopeType,
)
from app.reports.security import resolve_report_identity
from app.reports.service import get_report_service


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    token = os.getenv("REPORT_CLI_TOKEN", "").strip()
    if not token:
        parser.error("Configure REPORT_CLI_TOKEN no ambiente.")

    try:
        identity = resolve_report_identity(f"Bearer {token}")
        service = get_report_service()
        prepared = service.prepare(
            PrepareReportRequest(
                conversation_id=args.conversation_id or f"cli-{uuid4()}",
                report_type="executive_status",
                scope=ReportScope(type=ScopeType(args.scope_type), id=args.scope_id),
                period=ReportPeriod(
                    start_date=date.fromisoformat(args.start_date),
                    end_date=date.fromisoformat(args.end_date),
                    label=args.period_label,
                ),
                options=ReportOptions(
                    audience=Audience(args.audience),
                    purpose=Purpose(args.purpose),
                    emphasis=[Emphasis(item) for item in args.emphasis],
                    additional_context=args.additional_context,
                ),
            ),
            identity,
        )
        execution, created = service.create(
            CreateReportRequest(
                prepared_request=prepared.prepared_request,
                confirmation_hash=prepared.confirmation_hash,
                idempotency_key=args.idempotency_key
                or f"cli:{prepared.confirmation_hash}",
            ),
            identity,
        )
        if created and service.execution_mode == "local":
            service.process_local(execution.execution_id)
            execution = service.get(execution.execution_id, identity)
        print(service.response(execution).model_dump_json(indent=2))
        return 0
    except (ReportError, ValueError) as error:
        message = error.message if isinstance(error, ReportError) else str(error)
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera um relatorio executivo usando o duplo local controlado."
    )
    parser.add_argument(
        "--scope-type", choices=[item.value for item in ScopeType], required=True
    )
    parser.add_argument("--scope-id", required=True)
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--period-label")
    parser.add_argument(
        "--audience",
        choices=[item.value for item in Audience],
        default=Audience.PMO.value,
    )
    parser.add_argument(
        "--purpose",
        choices=[item.value for item in Purpose],
        default=Purpose.MONTHLY_GOVERNANCE.value,
    )
    parser.add_argument(
        "--emphasis",
        action="append",
        choices=[item.value for item in Emphasis],
        default=[],
    )
    parser.add_argument("--additional-context")
    parser.add_argument("--conversation-id")
    parser.add_argument("--idempotency-key")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
