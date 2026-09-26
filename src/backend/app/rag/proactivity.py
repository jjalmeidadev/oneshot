"""Resolve a intencao secundaria que orienta a sugestao proativa do RAG."""

from collections.abc import Callable
from dataclasses import dataclass
import json
import os
from pathlib import Path

from app.database.connection import (
    DatabaseConfigurationError,
    DatabaseConnectionError,
    open_database_connection,
)
from app.nlp.schemas import AudioIntent


DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "secondary_intents.json"
PUBLIC_LOOKUP_ERROR = "Nao foi possivel consultar a intencao secundaria."

SECONDARY_INTENT_QUERY = """
SELECT
    secondary.secondary_intent,
    secondary.description,
    secondary.rag_instruction,
    secondary.display_message
FROM public.secondary_intents secondary
JOIN public.intent_catalog catalog ON catalog.id = secondary.specific_intent_id
WHERE catalog.macro_intent = 'CONSULTA'
  AND catalog.specific_intent = %s
  AND catalog.is_active
  AND secondary.is_active
ORDER BY secondary.created_at, secondary.id
LIMIT 1;
"""


@dataclass(frozen=True)
class SecondaryIntent:
    name: str
    description: str
    rag_instruction: str
    display_message: str


def resolve_secondary_intent(
    intent: AudioIntent | None,
    *,
    connect: Callable[..., object] | None = None,
    catalog_path: Path | None = None,
) -> SecondaryIntent | None:
    """Retorna a sugestao compativel sem reclassificar a fala do usuario."""

    if not intent or intent.macro != "CONSULTA" or not intent.specific:
        return None

    if connect is None and not _database_is_configured():
        return _load_local_catalog(catalog_path).get(intent.specific)

    try:
        connection = open_database_connection(connect=connect)
        try:
            with connection.cursor() as cursor:
                cursor.execute(SECONDARY_INTENT_QUERY, (intent.specific,))
                row = cursor.fetchone()
        finally:
            connection.close()
    except DatabaseConfigurationError:
        raise
    except Exception as error:
        raise DatabaseConnectionError(PUBLIC_LOOKUP_ERROR) from error

    if not row:
        return None

    if isinstance(row, dict):
        return SecondaryIntent(
            name=str(row["secondary_intent"]),
            description=str(row["description"]),
            rag_instruction=str(row["rag_instruction"]),
            display_message=str(row["display_message"]),
        )

    return SecondaryIntent(
        name=str(row[0]),
        description=str(row[1]),
        rag_instruction=str(row[2]),
        display_message=str(row[3]),
    )


def _load_local_catalog(path: Path | None = None) -> dict[str, SecondaryIntent]:
    payload = json.loads((path or DEFAULT_CATALOG_PATH).read_text(encoding="utf-8"))
    return {
        specific_intent: SecondaryIntent(
            name=definition["secondary_intent"],
            description=definition["description"],
            rag_instruction=definition["rag_instruction"],
            display_message=definition["display_message"],
        )
        for specific_intent, definition in payload.items()
    }


def _database_is_configured() -> bool:
    return bool(
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("SUPABASE_DATABASE_URL", "").strip()
    )
