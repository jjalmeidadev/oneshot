"""Sugestoes proativas pendentes, vinculadas a identidade e conversa."""

from dataclasses import asdict, dataclass, replace
import json
import os
from threading import Lock
from time import monotonic
from typing import Any
from uuid import uuid4

from app.database.connection import open_database_connection
from app.rag.proactivity import SecondaryIntent
from app.rag.sharepoint import RetrievedDocument, SharePointDocument


DEFAULT_PENDING_TTL_SECONDS = 15 * 60


class PendingSuggestionNotFound(LookupError):
    """A sugestao nao existe, expirou, foi consumida ou pertence a outro escopo."""


class PendingSuggestionInProgress(RuntimeError):
    """A sugestao ja esta sendo confirmada por outra requisicao."""


class PendingSuggestionStorageError(RuntimeError):
    """Falha controlada no armazenamento compartilhado das sugestoes."""


@dataclass(frozen=True)
class PendingProactiveSuggestion:
    suggestion_id: str
    requester_id: str
    conversation_id: str
    original_message: str
    secondary_intent: SecondaryIntent
    sources: tuple[RetrievedDocument, ...]
    expires_at: float | None = None
    claimed: bool = False


_pending: dict[str, PendingProactiveSuggestion] = {}
_pending_lock = Lock()


def register_pending_suggestion(
    *,
    requester_id: str,
    conversation_id: str,
    original_message: str,
    secondary_intent: SecondaryIntent,
    sources: list[RetrievedDocument],
) -> str:
    """Persiste uma sugestao opaca, limitada ao usuario e conversa de origem."""

    suggestion_id = str(uuid4())
    pending = PendingProactiveSuggestion(
        suggestion_id=suggestion_id,
        requester_id=requester_id,
        conversation_id=conversation_id,
        original_message=original_message,
        secondary_intent=secondary_intent,
        sources=tuple(sources),
        expires_at=monotonic() + _pending_ttl_seconds(),
    )
    if _database_is_configured():
        _register_in_database(pending)
        return suggestion_id

    with _pending_lock:
        _discard_expired_locked()
        _pending[suggestion_id] = pending
    return suggestion_id


def decline_pending_suggestion(
    suggestion_id: str,
    *,
    requester_id: str,
    conversation_id: str,
) -> PendingProactiveSuggestion:
    """Consome a sugestao sem executar geracao secundaria."""

    if _database_is_configured():
        return _decline_in_database(suggestion_id, requester_id, conversation_id)

    with _pending_lock:
        _discard_expired_locked()
        pending = _bound_pending_locked(suggestion_id, requester_id, conversation_id)
        if pending.claimed:
            raise PendingSuggestionInProgress(suggestion_id)
        del _pending[suggestion_id]
        return pending


def claim_pending_suggestion(
    suggestion_id: str,
    *,
    requester_id: str,
    conversation_id: str,
) -> PendingProactiveSuggestion:
    """Reserva atomicamente a sugestao para uma unica execucao autorizada."""

    if _database_is_configured():
        return _claim_in_database(suggestion_id, requester_id, conversation_id)

    with _pending_lock:
        _discard_expired_locked()
        pending = _bound_pending_locked(suggestion_id, requester_id, conversation_id)
        if pending.claimed:
            raise PendingSuggestionInProgress(suggestion_id)
        claimed = replace(pending, claimed=True)
        _pending[suggestion_id] = claimed
        return claimed


def complete_pending_suggestion(pending: PendingProactiveSuggestion) -> None:
    if _database_is_configured():
        _mutate_database(
            """
            DELETE FROM public.pending_proactive_suggestions
            WHERE id = %s AND requester_id = %s AND external_conversation_id = %s;
            """,
            (pending.suggestion_id, pending.requester_id, pending.conversation_id),
        )
        return
    with _pending_lock:
        _pending.pop(pending.suggestion_id, None)


def release_pending_suggestion(pending: PendingProactiveSuggestion) -> None:
    """Permite nova tentativa quando o provedor falha antes de concluir."""

    if _database_is_configured():
        _mutate_database(
            """
            UPDATE public.pending_proactive_suggestions
            SET claimed_at = NULL
            WHERE id = %s AND requester_id = %s AND external_conversation_id = %s;
            """,
            (pending.suggestion_id, pending.requester_id, pending.conversation_id),
        )
        return
    with _pending_lock:
        current = _pending.get(pending.suggestion_id)
        if current is not None:
            _pending[pending.suggestion_id] = replace(current, claimed=False)


def clear_pending_suggestions() -> None:
    """Isola o fallback em memoria usado por desenvolvimento e testes."""

    with _pending_lock:
        _pending.clear()


def _bound_pending_locked(
    suggestion_id: str,
    requester_id: str,
    conversation_id: str,
) -> PendingProactiveSuggestion:
    pending = _pending.get(suggestion_id)
    if (
        pending is None
        or pending.requester_id != requester_id
        or pending.conversation_id != conversation_id
    ):
        raise PendingSuggestionNotFound(suggestion_id)
    return pending


def _register_in_database(pending: PendingProactiveSuggestion) -> None:
    _mutate_database(
        """
        INSERT INTO public.pending_proactive_suggestions (
            id, requester_id, external_conversation_id, original_message,
            secondary_intent, sources, expires_at
        )
        VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb,
                NOW() + (%s * INTERVAL '1 second'));
        """,
        (
            pending.suggestion_id,
            pending.requester_id,
            pending.conversation_id,
            pending.original_message,
            _json(asdict(pending.secondary_intent)),
            _json([asdict(source) for source in pending.sources]),
            _pending_ttl_seconds(),
        ),
    )


def _claim_in_database(
    suggestion_id: str,
    requester_id: str,
    conversation_id: str,
) -> PendingProactiveSuggestion:
    return _take_from_database(
        suggestion_id,
        requester_id,
        conversation_id,
        """
        UPDATE public.pending_proactive_suggestions
        SET claimed_at = NOW()
        WHERE id = %s AND requester_id = %s AND external_conversation_id = %s
          AND expires_at > NOW() AND claimed_at IS NULL
        RETURNING id::text, requester_id, external_conversation_id,
                  original_message, secondary_intent, sources;
        """,
    )


def _decline_in_database(
    suggestion_id: str,
    requester_id: str,
    conversation_id: str,
) -> PendingProactiveSuggestion:
    return _take_from_database(
        suggestion_id,
        requester_id,
        conversation_id,
        """
        DELETE FROM public.pending_proactive_suggestions
        WHERE id = %s AND requester_id = %s AND external_conversation_id = %s
          AND expires_at > NOW() AND claimed_at IS NULL
        RETURNING id::text, requester_id, external_conversation_id,
                  original_message, secondary_intent, sources;
        """,
    )


def _take_from_database(
    suggestion_id: str,
    requester_id: str,
    conversation_id: str,
    query: str,
) -> PendingProactiveSuggestion:
    try:
        connection = open_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (suggestion_id, requester_id, conversation_id))
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(
                        """
                        SELECT claimed_at IS NOT NULL
                        FROM public.pending_proactive_suggestions
                        WHERE id = %s AND requester_id = %s
                          AND external_conversation_id = %s AND expires_at > NOW();
                        """,
                        (suggestion_id, requester_id, conversation_id),
                    )
                    state = cursor.fetchone()
                    if state and bool(_first_value(state)):
                        raise PendingSuggestionInProgress(suggestion_id)
                    raise PendingSuggestionNotFound(suggestion_id)
            _commit(connection)
            return _pending_from_row(row)
        except (PendingSuggestionInProgress, PendingSuggestionNotFound):
            _rollback(connection)
            raise
        except Exception:
            _rollback(connection)
            raise
        finally:
            connection.close()
    except (PendingSuggestionInProgress, PendingSuggestionNotFound):
        raise
    except Exception as error:
        raise PendingSuggestionStorageError(
            "Nao foi possivel acessar as sugestoes pendentes."
        ) from error


def _mutate_database(query: str, params: tuple[object, ...]) -> None:
    try:
        connection = open_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
            _commit(connection)
        except Exception:
            _rollback(connection)
            raise
        finally:
            connection.close()
    except Exception as error:
        raise PendingSuggestionStorageError(
            "Nao foi possivel persistir a sugestao proativa."
        ) from error


def _pending_from_row(row: object) -> PendingProactiveSuggestion:
    if isinstance(row, dict):
        values = (
            row["id"], row["requester_id"], row["external_conversation_id"],
            row["original_message"], row["secondary_intent"], row["sources"],
        )
    else:
        values = tuple(row)
    secondary_payload = _json_value(values[4])
    sources_payload = _json_value(values[5])
    return PendingProactiveSuggestion(
        suggestion_id=str(values[0]),
        requester_id=str(values[1]),
        conversation_id=str(values[2]),
        original_message=str(values[3]),
        secondary_intent=SecondaryIntent(**secondary_payload),
        sources=tuple(
            RetrievedDocument(
                document=SharePointDocument(**source["document"]),
                score=float(source["score"]),
            )
            for source in sources_payload
        ),
        claimed=True,
    )


def _discard_expired_locked() -> None:
    now = monotonic()
    expired = [
        key for key, value in _pending.items()
        if value.expires_at is not None and value.expires_at <= now
    ]
    for key in expired:
        del _pending[key]


def _database_is_configured() -> bool:
    return bool(
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("SUPABASE_DATABASE_URL", "").strip()
    )


def _pending_ttl_seconds() -> int:
    try:
        return min(max(int(os.getenv("PROACTIVE_SUGGESTION_TTL_SECONDS", "")), 30), 3600)
    except ValueError:
        return DEFAULT_PENDING_TTL_SECONDS


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _json_value(value: Any) -> Any:
    return json.loads(value) if isinstance(value, str) else value


def _first_value(row: object) -> object:
    if isinstance(row, dict):
        return next(iter(row.values()))
    return row[0]


def _commit(connection: Any) -> None:
    commit = getattr(connection, "commit", None)
    if commit:
        commit()


def _rollback(connection: Any) -> None:
    rollback = getattr(connection, "rollback", None)
    if rollback:
        rollback()
