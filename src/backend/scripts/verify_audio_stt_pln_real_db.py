"""Smoke test controlado de audio -> STT -> PLN -> PostgreSQL real.

Cria evidencias sinteticas de sucesso e falha, valida os campos persistidos e
remove todos os registros criados antes de encerrar.
"""

from __future__ import annotations

from io import BytesIO
import os
import struct
from uuid import uuid4
import wave

from fastapi.testclient import TestClient

from app.audio import transcription
from app.database.connection import open_database_connection
from app.gemini.schemas import GeminiChatResponse, GeminiUsage
from app.main import app
import app.nlp.inference as inference
import app.pipeline as pipeline


TOKEN = "s4-13-real-db-token"
AUTH_HEADER = {"Authorization": f"Bearer {TOKEN}"}
TRANSCRIPT = "qual é o status da extensão da Linha 5-Lilás?"


def _wav() -> bytes:
    frames = b"".join(
        struct.pack("<h", 8_000 if (index // 40) % 2 == 0 else -8_000)
        for index in range(16_000)
    )
    output = BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16_000)
        audio.writeframes(frames)
    return output.getvalue()


async def _transcribe(*_args: object, **_kwargs: object):
    return transcription.Transcription(
        text=TRANSCRIPT,
        confidence=0.97,
        duration_seconds=1,
    )


def _provider(_request, intent=None, entities=None) -> GeminiChatResponse:
    return GeminiChatResponse(
        text="Resposta sintetica controlada para S4-13.",
        model="smoke-test-boundary",
        interaction_id="provider-smoke-test",
        latency_ms=1,
        usage=GeminiUsage(),
    )


def _post(conversation_id: str):
    with TestClient(app) as client:
        return client.post(
            "/api/audio",
            files={"audio": ("s4-13.wav", _wav(), "audio/wav")},
            headers=AUTH_HEADER,
            data={
                "conversation_id": conversation_id,
                "use_intent_classifier": "true",
            },
        )


def _evidence(conversation_id: str) -> dict[str, object]:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute(
                """
                SELECT
                    c.id::text,
                    c.channel,
                    c.external_conversation_id,
                    i.id::text,
                    i.intent_id IS NOT NULL,
                    i.user_prompt,
                    i.macro_intent_predicted,
                    i.specific_intent_predicted,
                    i.handler_selected,
                    i.route_taken,
                    i.processing_status,
                    i.macro_intent_confidence,
                    i.specific_intent_confidence
                FROM public.ai_conversations c
                JOIN public.ai_interactions i ON i.conversation_id = c.id
                WHERE c.channel = 'api'
                  AND c.external_conversation_id = %s
                ORDER BY i.created_at DESC
                LIMIT 1;
                """,
                (conversation_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise AssertionError("Interacao sintetica nao foi persistida.")
            cursor.execute(
                """
                SELECT event_type, component, event_status
                FROM public.audit_events
                WHERE interaction_id = %s::uuid;
                """,
                (row[3],),
            )
            events = set(cursor.fetchall())
            return {"row": row, "events": events}
    finally:
        connection.rollback()
        connection.close()


def _cleanup(conversation_ids: list[str]) -> None:
    connection = open_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT i.id
                FROM public.ai_interactions i
                JOIN public.ai_conversations c ON c.id = i.conversation_id
                WHERE c.channel = 'api'
                  AND c.external_conversation_id = ANY(%s);
                """,
                (conversation_ids,),
            )
            interaction_ids = [row[0] for row in cursor.fetchall()]
            if interaction_ids:
                cursor.execute(
                    "DELETE FROM public.audit_events WHERE interaction_id = ANY(%s);",
                    (interaction_ids,),
                )
            cursor.execute(
                """
                DELETE FROM public.ai_conversations
                WHERE channel = 'api'
                  AND external_conversation_id = ANY(%s);
                """,
                (conversation_ids,),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main() -> None:
    success_id = f"s4-13-success-{uuid4()}"
    failure_id = f"s4-13-failure-{uuid4()}"
    conversation_ids = [success_id, failure_id]
    original_identity_map = os.environ.get("AUDIO_SIMULATED_IDENTITIES")
    original_transcribe = transcription.transcribe
    original_provider = pipeline.generate_chat_response
    original_classifier = inference.classify

    os.environ["AUDIO_SIMULATED_IDENTITIES"] = f"{TOKEN}=s4-13-smoke-user"
    transcription.transcribe = _transcribe
    pipeline.generate_chat_response = _provider

    try:
        success_response = _post(success_id)
        assert success_response.status_code == 200, success_response.text
        success = _evidence(success_id)
        success_row = success["row"]
        success_events = success["events"]
        assert success_row[1] == "api"
        assert success_row[2] == success_id
        assert success_row[4] is True
        assert success_row[5] == TRANSCRIPT
        assert success_row[6] == "CONSULTA"
        assert success_row[7] == "consulta_status_projeto"
        assert success_row[8] == "handler:consulta_status_projeto"
        assert success_row[9] == "sharepoint_query"
        assert success_row[10] == "processado"
        assert 0 <= float(success_row[11]) <= 1
        assert 0 <= float(success_row[12]) <= 1
        assert ("pln_intent_classified", "pln", "sucesso") in success_events
        assert ("database_traceability_recorded", "database", "sucesso") in success_events

        def fail_classifier(_text: str):
            raise RuntimeError("s4-13-controlled-classifier-failure")

        inference.classify = fail_classifier
        failure_response = _post(failure_id)
        assert failure_response.status_code == 503, failure_response.text
        assert failure_response.json()["error"]["code"] == "PROCESSING_UNAVAILABLE"
        failure = _evidence(failure_id)
        failure_row = failure["row"]
        failure_events = failure["events"]
        assert failure_row[2] == failure_id
        assert failure_row[4] is False
        assert failure_row[5] == TRANSCRIPT
        assert failure_row[6] is None
        assert failure_row[7] is None
        assert failure_row[10] == "erro"
        assert ("pipeline_controlled_failure", "api", "falha") in failure_events
        assert ("database_traceability_recorded", "database", "sucesso") in failure_events

        print("REAL_DB_SUCCESS_FLOW_OK=True")
        print("REAL_DB_FAILURE_FLOW_OK=True")
        print("REAL_DB_CORRELATION_OK=True")
        print("REAL_DB_AUDIT_OK=True")
    finally:
        inference.classify = original_classifier
        pipeline.generate_chat_response = original_provider
        transcription.transcribe = original_transcribe
        if original_identity_map is None:
            os.environ.pop("AUDIO_SIMULATED_IDENTITIES", None)
        else:
            os.environ["AUDIO_SIMULATED_IDENTITIES"] = original_identity_map
        _cleanup(conversation_ids)
        print("REAL_DB_CLEANUP_OK=True")


if __name__ == "__main__":
    main()
