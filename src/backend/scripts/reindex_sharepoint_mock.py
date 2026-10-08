"""Aplica ou valida a carga documental do SharePoint simulado."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from app.rag.reindex import reindex_sharepoint_mock, sharepoint_mock_status


def _load_environment() -> None:
    script_path = Path(__file__).resolve()
    load_dotenv(script_path.parents[1] / ".env", override=False)
    load_dotenv(script_path.parents[3] / ".env", override=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("apply", "status"),
        help="apply reaplica a carga; status apenas valida a cobertura atual.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _load_environment()
    result = (
        reindex_sharepoint_mock()
        if args.command == "apply"
        else sharepoint_mock_status()
    )
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
