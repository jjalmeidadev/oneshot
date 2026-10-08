"""Processos independentes da integração SharePoint/RabbitMQ."""

from __future__ import annotations

import argparse
import asyncio
import json
import os

from dotenv import load_dotenv

from app.sharepoint_webhooks.publisher import publish_pending_sharepoint_once
from app.sharepoint_webhooks.consumer import run_sharepoint_consumer


async def run_publisher() -> None:
    interval = max(
        float(os.getenv("SHAREPOINT_WEBHOOK_PUBLISHER_POLL_SECONDS", "2")),
        0.25,
    )
    while True:
        published = await publish_pending_sharepoint_once()
        if published == 0:
            await asyncio.sleep(interval)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("publisher-once", "publisher", "consumer")
    )
    args = parser.parse_args()
    if args.command == "publisher-once":
        print(json.dumps({"published": asyncio.run(publish_pending_sharepoint_once())}))
        return 0
    if args.command == "publisher":
        asyncio.run(run_publisher())
        return 0
    asyncio.run(run_sharepoint_consumer())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
