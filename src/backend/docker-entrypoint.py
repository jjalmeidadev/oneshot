"""Validate runtime-only demo configuration before starting the API."""

from __future__ import annotations

import json
import os
import sys


def fail(message: str) -> None:
    print(f"Docker runtime configuration error: {message}", file=sys.stderr)
    raise SystemExit(64)


def runtime_command() -> list[str]:
    """Mantém o VHS em um único processo até existir cache compartilhado."""

    return [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--workers",
        "1",
        "--no-access-log",
    ]


def main() -> None:
    audio_entries = [
        item.strip()
        for item in os.getenv("AUDIO_SIMULATED_IDENTITIES", "").split(",")
        if item.strip()
    ]
    if not audio_entries or any(
        not separator or not token.strip() or not identity.strip()
        for token, separator, identity in (item.partition("=") for item in audio_entries)
    ):
        fail("configure AUDIO_SIMULATED_IDENTITIES as token=entra_object_id.")

    raw_report_identities = os.getenv("REPORT_SIMULATED_IDENTITIES", "").strip()
    try:
        report_identities = json.loads(raw_report_identities)
    except json.JSONDecodeError:
        fail("configure REPORT_SIMULATED_IDENTITIES as a non-empty JSON object.")
    if not isinstance(report_identities, dict) or not report_identities:
        fail("configure REPORT_SIMULATED_IDENTITIES as a non-empty JSON object.")
    if any(
        not isinstance(identity, dict)
        or not identity.get("subject")
        or not identity.get("role")
        for identity in report_identities.values()
    ):
        fail("each report identity must include subject and role.")

    if not os.getenv("GEMINI_API_KEY", "").strip():
        fail("configure GEMINI_API_KEY in the runtime environment.")
    if not os.getenv("AZURE_SPEECH_KEY", "").strip():
        fail("configure AZURE_SPEECH_KEY in the runtime environment.")
    if not any(
        os.getenv(name, "").strip()
        for name in ("AZURE_SPEECH_RESOURCE", "AZURE_SPEECH_ENDPOINT")
    ):
        fail("configure AZURE_SPEECH_RESOURCE or AZURE_SPEECH_ENDPOINT.")

    os.execvp("uvicorn", runtime_command())


if __name__ == "__main__":
    main()
