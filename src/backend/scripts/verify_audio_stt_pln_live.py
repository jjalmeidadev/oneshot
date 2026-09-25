"""Verifica audio real -> Azure STT -> PLN -> PostgreSQL/Supabase.

O arquivo de audio e fornecido localmente e nunca e copiado para o repositorio.
A interacao sintetica criada para a verificacao e removida ao final.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import os
from pathlib import Path
from statistics import median
import unicodedata
from uuid import uuid4

from fastapi.testclient import TestClient

from app.audio import transcription
from app.database.connection import open_database_connection
from app.gemini.schemas import GeminiChatResponse, GeminiUsage
from app.main import app
import app.pipeline as pipeline
from scripts.verify_audio_stt_pln_real_db import (
    AUTH_HEADER,
    TOKEN,
    _cleanup,
    _evidence,
)


def _normalized(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa a cadeia real de audio, STT, PLN e persistencia.",
    )
    parser.add_argument("audio_file", type=Path)
    parser.add_argument(
        "--expected-term",
        action="append",
        default=[],
        help="Termo que deve aparecer na transcricao; pode ser repetido.",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="Quantidade de envios identicos; minimo 2 para comprovar miss e hit.",
    )
    return parser.parse_args()


def _controlled_provider(_request, intent=None, entities=None) -> GeminiChatResponse:
    """Isola a geracao, que ocorre depois da cadeia coberta pela S4-13."""

    return GeminiChatResponse(
        text="Resposta controlada apos STT e PLN reais.",
        model="s4-13-live-boundary",
        interaction_id="s4-13-live-provider",
        latency_ms=1,
        usage=GeminiUsage(),
    )


def _residue_count(conversation_id: str) -> int:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM public.ai_conversations
                WHERE channel = 'api'
                  AND external_conversation_id = %s;
                """,
                (conversation_id,),
            )
            return int(cursor.fetchone()[0])
    finally:
        connection.rollback()
        connection.close()


def _delta(after: dict[str, int], before: dict[str, int]) -> dict[str, int]:
    return {name: after[name] - before[name] for name in after}


def _p95(values: list[int]) -> int:
    ordered = sorted(values)
    index = max(0, (95 * len(ordered) + 99) // 100 - 1)
    return ordered[index]


def main() -> None:
    arguments = _arguments()
    if arguments.repetitions < 2:
        raise SystemExit("--repetitions deve ser pelo menos 2.")
    if os.getenv("VHS_ENABLED", "1").strip() == "0":
        raise SystemExit("VHS_ENABLED=0; habilite o cache para esta verificacao.")
    audio_path = arguments.audio_file.resolve(strict=True)
    audio_bytes = audio_path.read_bytes()
    conversation_id = f"s4-13-live-{uuid4()}"
    original_identity_map = os.environ.get("AUDIO_SIMULATED_IDENTITIES")
    original_provider = pipeline.generate_chat_response
    os.environ["AUDIO_SIMULATED_IDENTITIES"] = f"{TOKEN}=s4-13-live-user"
    pipeline.generate_chat_response = _controlled_provider

    try:
        transcription.response_cache.invalidate()
        metrics_before = transcription.response_cache.metrics()
        payloads = []
        with TestClient(app) as client:
            for _ in range(arguments.repetitions):
                response = client.post(
                    "/api/audio",
                    files={"audio": (audio_path.name, audio_bytes, "audio/wav")},
                    headers=AUTH_HEADER,
                    data={
                        "conversation_id": conversation_id,
                        "language": "pt-BR",
                        "use_intent_classifier": "true",
                    },
                )
                assert response.status_code == 200, response.text
                payloads.append(response.json())

        payload = payloads[0]
        transcript = payload["transcription"]["text"]
        intent = payload["intent"]
        assert transcript.strip(), "Azure STT retornou transcricao vazia."
        assert intent is not None, "PLN nao retornou classificacao."
        assert all(
            item["transcription"] == payload["transcription"] for item in payloads
        ), "O hit nao reproduziu a mesma transcricao."

        normalized_transcript = _normalized(transcript)
        for term in arguments.expected_term:
            assert _normalized(term) in normalized_transcript, (
                f"Termo esperado ausente da transcricao: {term!r}."
            )

        evidence = _evidence(conversation_id)
        row = evidence["row"]
        events = evidence["events"]
        assert row[1] == "api"
        assert row[2] == conversation_id
        assert row[5] == transcript
        assert row[6] == intent["macro"]
        assert (row[7] or "") == intent["specific"]
        assert any(event[0] == "pln_intent_classified" for event in events)
        assert ("database_traceability_recorded", "database", "sucesso") in events

        metrics_delta = _delta(
            transcription.response_cache.metrics(), metrics_before
        )
        assert metrics_delta["miss"] == 1
        assert metrics_delta["record"] == 1
        assert metrics_delta["provider_call"] == 1
        assert metrics_delta["hit"] == arguments.repetitions - 1
        assert metrics_delta["provider_error"] == 0
        stt_times = [item["pipeline_metrics"]["stt_ms"] for item in payloads]
        hit_times = stt_times[1:]

        print(f"LIVE_AUDIO_SHA256={sha256(audio_bytes).hexdigest()}")
        print(f"LIVE_STT_TRANSCRIPT_SHA256={sha256(transcript.encode()).hexdigest()}")
        print(f"LIVE_PLN_MACRO={intent['macro']}")
        print(f"LIVE_PLN_SPECIFIC={intent['specific']}")
        print(f"LIVE_VHS_WORKER_ID={transcription.VHS_WORKER_ID}")
        print(f"LIVE_VHS_REPETITIONS={arguments.repetitions}")
        print(f"LIVE_VHS_PROVIDER_CALLS={metrics_delta['provider_call']}")
        print(f"LIVE_VHS_CALLS_AVOIDED={metrics_delta['hit']}")
        print(f"LIVE_VHS_HIT_RATIO={metrics_delta['hit'] / arguments.repetitions:.4f}")
        print(f"LIVE_VHS_MISS_STT_MS={stt_times[0]}")
        print(f"LIVE_VHS_HIT_STT_MEDIAN_MS={median(hit_times):.1f}")
        print(f"LIVE_VHS_HIT_STT_P95_MS={_p95(hit_times)}")
        print("LIVE_DB_CORRELATION_OK=True")
        print("LIVE_DB_AUDIT_OK=True")
    finally:
        pipeline.generate_chat_response = original_provider
        if original_identity_map is None:
            os.environ.pop("AUDIO_SIMULATED_IDENTITIES", None)
        else:
            os.environ["AUDIO_SIMULATED_IDENTITIES"] = original_identity_map
        _cleanup([conversation_id])
        residue_count = _residue_count(conversation_id)
        assert residue_count == 0, "A verificacao deixou residuos no banco."
        print("LIVE_DB_CLEANUP_OK=True")
        print(f"LIVE_DB_RESIDUE_COUNT={residue_count}")


if __name__ == "__main__":
    main()
