"""Persistencia de rastreabilidade RNF03 para interacoes do pipeline."""

import json
import os
import re
from collections.abc import Callable
from typing import Any

from app.database.connection import open_database_connection
from app.gemini.schemas import GeminiChatRequest, GeminiChatResponse
from app.nlp.schemas import AudioIntent, PublicEntity

PUBLIC_TRACING_ERROR_MESSAGE = "Nao foi possivel registrar a rastreabilidade."


class TraceabilityError(RuntimeError):
    """Erro controlado de persistencia de rastreabilidade."""


def is_tracing_configured() -> bool:
    return bool(
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("SUPABASE_DATABASE_URL", "").strip()
    )


def trace_interaction(
    *,
    request: GeminiChatRequest,
    response: GeminiChatResponse | None,
    intent: AudioIntent | None,
    entities: list[PublicEntity],
    processing_ms: int,
    channel: str = "api",
    external_conversation_id: str | None = None,
    error_message: str | None = None,
    requester_id: str | None = None,
    connect: Callable[..., Any] | None = None,
) -> str | None:
    """Grava conversa, interacao, fontes persistidas e eventos de auditoria."""

    if connect is None and not is_tracing_configured():
        return None

    try:
        connection = open_database_connection(connect=connect)
        try:
            with connection.cursor() as cursor:
                user_id = _find_user_id(cursor, requester_id)
                intent_id = _find_intent_id(cursor, intent)
                conversation_id = _get_or_create_conversation(
                    cursor,
                    request,
                    channel,
                    external_conversation_id=external_conversation_id,
                    user_id=user_id,
                    requester_id=requester_id,
                )
                status = _processing_status(intent, response, error_message)
                limitation_response = _limitation_response(intent, response, error_message)
                interaction_id = _insert_interaction(
                    cursor,
                    conversation_id=conversation_id,
                    request=request,
                    response=response,
                    intent=intent,
                    intent_id=intent_id,
                    user_id=user_id,
                    status=status,
                    limitation_response=limitation_response,
                    processing_ms=processing_ms,
                )
                _insert_consulted_sources(cursor, interaction_id, response)
                _insert_audit_events(
                    cursor,
                    interaction_id=interaction_id,
                    request=request,
                    response=response,
                    intent=intent,
                    entities=entities,
                    status=status,
                    error_message=error_message,
                    user_id=user_id,
                    requester_id=requester_id,
                )
            _commit(connection)
            return interaction_id
        except Exception:
            _rollback(connection)
            raise
        finally:
            connection.close()
    except Exception as error:
        raise TraceabilityError(PUBLIC_TRACING_ERROR_MESSAGE) from error


def _find_intent_id(cursor: Any, intent: AudioIntent | None) -> str | None:
    if not intent or not intent.specific:
        return None

    cursor.execute(
        """
        SELECT id::text
        FROM public.intent_catalog
        WHERE macro_intent = %s
          AND specific_intent = %s
          AND is_active = TRUE
        LIMIT 1;
        """,
        (intent.macro, intent.specific),
    )
    return _first(cursor.fetchone())


def _find_user_id(cursor: Any, requester_id: str | None) -> str | None:
    if not requester_id:
        return None
    cursor.execute(
        """
        SELECT id::text
        FROM public.users
        WHERE entra_object_id = %s AND is_active = TRUE
        LIMIT 1;
        """,
        (requester_id,),
    )
    return _first(cursor.fetchone())


def _get_or_create_conversation(
    cursor: Any,
    request: GeminiChatRequest,
    channel: str,
    *,
    external_conversation_id: str | None = None,
    user_id: str | None,
    requester_id: str | None,
) -> str:
    external_id = external_conversation_id or request.conversation_id
    if external_id:
        cursor.execute(
            """
            SELECT id::text
            FROM public.ai_conversations
            WHERE channel = %s
              AND external_conversation_id = %s
              AND metadata->>'requester_id' IS NOT DISTINCT FROM %s
              AND conversation_status = 'ativa'
            ORDER BY started_at DESC
            LIMIT 1;
            """,
            (channel, external_id, requester_id),
        )
        row = cursor.fetchone()
        if row:
            return str(_first(row))

    cursor.execute(
        """
        INSERT INTO public.ai_conversations (
            user_id,
            channel,
            external_conversation_id,
            metadata
        )
        VALUES (%s, %s, %s, %s::jsonb)
        RETURNING id::text;
        """,
        (
            user_id,
            channel,
            external_id,
            _json({
                "source": "backend_pipeline",
                "rn_f": "RNF03",
                "requester_id": requester_id,
            }),
        ),
    )
    return str(_first(cursor.fetchone()))


def _insert_interaction(
    cursor: Any,
    *,
    conversation_id: str,
    request: GeminiChatRequest,
    response: GeminiChatResponse | None,
    intent: AudioIntent | None,
    intent_id: str | None,
    user_id: str | None,
    status: str,
    limitation_response: str | None,
    processing_ms: int,
) -> str:
    cursor.execute(
        """
        INSERT INTO public.ai_interactions (
            conversation_id,
            intent_id,
            user_prompt,
            normalized_prompt,
            macro_intent_predicted,
            macro_intent_confidence,
            specific_intent_predicted,
            specific_intent_confidence,
            handler_selected,
            route_taken,
            top_k_alternatives,
            response_text,
            limitation_response,
            processing_status,
            processing_ms,
            user_id
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s
        )
        RETURNING id::text;
        """,
        (
            conversation_id,
            intent_id,
            request.message,
            _normalize_prompt(request.message),
            _macro_intent_for_insert(intent),
            intent.confidence_macro if intent else None,
            intent.specific if intent and intent.specific else None,
            intent.confidence_specific if intent else None,
            intent.handler if intent else None,
            _route_taken(intent, response),
            _json(_alternatives(intent)),
            response.text if response else None,
            limitation_response,
            status,
            processing_ms,
            user_id,
        ),
    )
    return str(_first(cursor.fetchone()))


def _insert_consulted_sources(
    cursor: Any,
    interaction_id: str,
    response: GeminiChatResponse | None,
) -> None:
    if not response:
        return

    for order, source in enumerate(response.trace_sources, start=1):
        metadata = dict(source.get("metadata") or {})
        if metadata.get("fallback"):
            continue

        cursor.execute(
            """
            INSERT INTO public.consulted_sources (
                interaction_id,
                artifact_id,
                extract_id,
                project_id,
                source_type,
                source_title,
                source_url,
                source_locator,
                relevance_score,
                citation_order,
                metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb);
            """,
            (
                interaction_id,
                source.get("artifact_id"),
                source.get("extract_id"),
                source.get("project_id"),
                source.get("source_type") or "lista_sharepoint",
                source.get("source_title"),
                source.get("source_url"),
                source.get("source_locator"),
                source.get("relevance_score"),
                source.get("citation_order") or order,
                _json(metadata),
            ),
        )


def _insert_audit_events(
    cursor: Any,
    *,
    interaction_id: str,
    request: GeminiChatRequest,
    response: GeminiChatResponse | None,
    intent: AudioIntent | None,
    entities: list[PublicEntity],
    status: str,
    error_message: str | None,
    user_id: str | None,
    requester_id: str | None,
) -> None:
    events = [
        (
            "api_interaction_processed",
            "api",
            "falha" if status == "erro" else "sucesso",
            {
                "message_length": len(request.message),
                "has_response": response is not None,
                "processing_status": status,
                "requester_id": requester_id,
            },
        )
    ]

    if intent:
        events.append(
            (
                "pln_intent_classified",
                "pln",
                "sucesso"
                if status not in {"sem_confianca", "fora_escopo"}
                else "bloqueado",
                {
                    "macro": intent.macro,
                    "specific": intent.specific,
                    "handler": intent.handler,
                    "entities": [entity.model_dump() for entity in entities],
                },
            )
        )

    if response is not None:
        if response.workflow:
            events.append(
                (
                    "guided_workflow_dispatched",
                    "guided_workflow",
                    "pendente",
                    {
                        "action": response.workflow.action,
                        "workflow": response.workflow.workflow,
                        "contract_version": response.workflow.contract_version,
                    },
                )
            )
        else:
            events.append(
                (
                    "database_rag_sources_retrieved",
                    "database",
                    "sucesso" if response.sources else "pendente",
                    {
                        "source_count": len(response.sources),
                        "persistent_source_count": _persistent_source_count(response),
                        "retrieval_ms": response.retrieval_ms,
                    },
                )
            )

    if error_message:
        events.append(
            (
                "pipeline_controlled_failure",
                "api",
                "falha",
                {"message": _safe_error_message(error_message)},
            )
        )

    events.append(
        (
            "database_traceability_recorded",
            "database",
            "sucesso",
            {"rn_f": "RNF03"},
        )
    )

    for event_type, component, event_status, payload in events:
        cursor.execute(
            """
            INSERT INTO public.audit_events (
                interaction_id,
                event_type,
                component,
                event_status,
                user_id,
                event_payload
            )
            VALUES (%s, %s, %s, %s, %s, %s::jsonb);
            """,
            (
                interaction_id,
                event_type,
                component,
                event_status,
                user_id,
                _json(payload),
            ),
        )


def _processing_status(
    intent: AudioIntent | None,
    response: GeminiChatResponse | None,
    error_message: str | None,
) -> str:
    if error_message:
        return "erro"
    if intent and intent.macro == "FORA_DE_ESCOPO":
        return "fora_escopo"
    if intent and (intent.macro == "INDEFINIDA" or not intent.specific):
        return "sem_confianca"
    return "processado"


def _macro_intent_for_insert(intent: AudioIntent | None) -> str | None:
    if not intent or intent.macro == "INDEFINIDA":
        return None
    return intent.macro


def _limitation_response(
    intent: AudioIntent | None,
    response: GeminiChatResponse | None,
    error_message: str | None,
) -> str | None:
    if error_message:
        return _safe_error_message(error_message)
    if response and (
        response.model in {"classificador-local", "rag-retriever"}
        or (intent and intent.macro in {"FORA_DE_ESCOPO", "INDEFINIDA"})
    ):
        return response.text
    return None


def _route_taken(
    intent: AudioIntent | None,
    response: GeminiChatResponse | None,
) -> str:
    if intent and intent.macro in {"FORA_DE_ESCOPO", "INDEFINIDA"}:
        return "fora_escopo"
    if response and response.workflow and response.workflow.action == "start":
        return "guided_workflow"
    if response and response.sources:
        return "sharepoint_query"
    if intent and intent.macro == "CONSULTA":
        return "sharepoint_query"
    return "analise_local"


def _alternatives(intent: AudioIntent | None) -> list[dict]:
    if not intent:
        return []
    return [alternative.model_dump() for alternative in intent.alternatives]


def _persistent_source_count(response: GeminiChatResponse) -> int:
    return sum(
        1
        for source in response.trace_sources
        if not (source.get("metadata") or {}).get("fallback")
    )


def _normalize_prompt(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _safe_error_message(value: str) -> str:
    if "database" in value.lower() or "banco" in value.lower():
        return "Falha controlada de banco de dados."
    return "Falha controlada no processamento."


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _first(row: object) -> str | None:
    if row is None:
        return None
    if isinstance(row, dict):
        return row.get("id")
    return row[0]


def _commit(connection: Any) -> None:
    commit = getattr(connection, "commit", None)
    if commit:
        commit()


def _rollback(connection: Any) -> None:
    rollback = getattr(connection, "rollback", None)
    if rollback:
        rollback()
