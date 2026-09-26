"""Retoma execucoes de relatorio persistidas em queued/processing.

Uso recomendado pelo agendador do ambiente:
    python -m scripts.recover_report_jobs --stale-after-seconds 60 --limit 50
"""

from __future__ import annotations

import argparse
import json

from dotenv import load_dotenv

from app.reports.service import get_report_service


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stale-after-seconds", type=int, default=60)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    load_dotenv()
    recovered = get_report_service().recover_pending(
        stale_after_seconds=args.stale_after_seconds,
        limit=args.limit,
    )
    print(json.dumps({"recovered": recovered, "count": len(recovered)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
