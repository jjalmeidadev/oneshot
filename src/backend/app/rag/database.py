"""Recuperacao RAG em PostgreSQL/Supabase sobre extratos consultaveis."""

from collections.abc import Callable, Iterable
import os

from app.database.connection import (
    DatabaseConfigurationError,
    DatabaseConnectionError,
    open_database_connection,
)
from app.nlp.schemas import AudioIntent, PublicEntity
from app.rag.sharepoint import (
    RetrievedDocument,
    SharePointDocument,
    _configured_result_limit,
    _meaningful_tokens,
)

PUBLIC_RAG_DATABASE_ERROR_MESSAGE = (
    "Nao foi possivel recuperar contexto no banco de dados."
)

RAG_DATABASE_QUERY = """
WITH query_terms AS (
    SELECT unnest(%s::text[]) AS term
),
entity_terms AS (
    SELECT unnest(%s::text[]) AS term
)
SELECT
    se.id::text AS extract_id,
    a.id::text AS artifact_id,
    COALESCE(se.project_id, a.project_id)::text AS project_id,
    a.partner_source_id,
    a.title AS artifact_title,
    a.sharepoint_library,
    a.sharepoint_url,
    COALESCE(a.extracted_at, se.updated_at, se.created_at) AS last_modified,
    se.content_text,
    se.source_locator,
    p.code AS project_code,
    p.title AS project_title,
    COALESCE(
        (
            SELECT SUM(
            CASE
                WHEN se.content_text ILIKE '%%' || query_terms.term || '%%'
                    OR a.title ILIKE '%%' || query_terms.term || '%%'
                    OR COALESCE(a.description, '') ILIKE '%%' || query_terms.term || '%%'
                    OR COALESCE(a.metadata -> 'fields' ->> 'PalavrasChave', '') ILIKE '%%' || query_terms.term || '%%'
                THEN 1.0
                ELSE 0.0
            END
            )
            FROM query_terms
        ),
        0.0
    )
    + COALESCE(
        (
            SELECT SUM(
            CASE
                WHEN COALESCE(p.code, '') ILIKE '%%' || entity_terms.term || '%%'
                    OR COALESCE(p.title, '') ILIKE '%%' || entity_terms.term || '%%'
                    OR COALESCE(a.metadata -> 'fields' ->> 'Linha', '') ILIKE '%%' || entity_terms.term || '%%'
                    OR se.content_text ILIKE '%%' || entity_terms.term || '%%'
                THEN 2.0
                ELSE 0.0
            END
            )
            FROM entity_terms
        ),
        0.0
    )
    + CASE
        WHEN %s = 'consulta_status_projeto'
            AND COALESCE(a.source_status_label, se.metadata ->> 'status', '') <> ''
        THEN 1.0
        WHEN %s = 'consulta_cronograma_prazo'
            AND (
                se.content_text ILIKE '%%prazo%%'
                OR se.content_text ILIKE '%%cronograma%%'
                OR se.content_text ILIKE '%%periodo%%'
                OR se.metadata ? 'validity'
            )
        THEN 1.0
        WHEN %s = 'consulta_riscos_projeto'
            AND (
                se.content_text ILIKE '%%risco%%'
                OR se.content_text ILIKE '%%problema%%'
                OR se.content_text ILIKE '%%falha%%'
                OR se.content_text ILIKE '%%manutencao%%'
            )
        THEN 1.0
        ELSE 0.0
    END AS score
FROM public.source_extracts se
JOIN public.project_artifacts a ON a.id = se.artifact_id
LEFT JOIN public.projects p ON p.id = COALESCE(se.project_id, a.project_id)
WHERE
    COALESCE(a.metadata ->> 'mock', se.metadata ->> 'mock') = 'true'
    AND (
        EXISTS (
            SELECT 1
            FROM query_terms
            WHERE se.content_text ILIKE '%%' || query_terms.term || '%%'
                OR a.title ILIKE '%%' || query_terms.term || '%%'
                OR COALESCE(a.description, '') ILIKE '%%' || query_terms.term || '%%'
                OR COALESCE(a.metadata -> 'fields' ->> 'PalavrasChave', '') ILIKE '%%' || query_terms.term || '%%'
        )
        OR EXISTS (
            SELECT 1
            FROM entity_terms
            WHERE COALESCE(p.code, '') ILIKE '%%' || entity_terms.term || '%%'
                OR COALESCE(p.title, '') ILIKE '%%' || entity_terms.term || '%%'
                OR COALESCE(a.metadata -> 'fields' ->> 'Linha', '') ILIKE '%%' || entity_terms.term || '%%'
                OR se.content_text ILIKE '%%' || entity_terms.term || '%%'
        )
    )
ORDER BY score DESC, a.title ASC, se.id ASC
LIMIT %s;
"""


def is_database_rag_configured() -> bool:
    return bool(
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("SUPABASE_DATABASE_URL", "").strip()
    )


def retrieve_database_context(
    query: str,
    intent: AudioIntent | None = None,
    entities: Iterable[PublicEntity] | None = None,
    limit: int | None = None,
    connect: Callable[..., object] | None = None,
) -> list[RetrievedDocument]:
    """Recupera extratos do banco usando pergunta, intencao e entidades."""

    query_terms = sorted(_expand_query_terms(query, intent))
    entity_terms = sorted(_entity_terms(entities or []))
    if not query_terms and not entity_terms:
        return []

    result_limit = limit if limit is not None else _configured_result_limit()
    specific_intent = intent.specific if intent else ""

    try:
        connection = open_database_connection(connect=connect)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    RAG_DATABASE_QUERY,
                    (
                        query_terms,
                        entity_terms,
                        specific_intent,
                        specific_intent,
                        specific_intent,
                        result_limit,
                    ),
                )
                return [_row_to_result(row) for row in cursor.fetchall()]
        finally:
            connection.close()
    except DatabaseConfigurationError:
        raise
    except Exception as error:
        raise DatabaseConnectionError(PUBLIC_RAG_DATABASE_ERROR_MESSAGE) from error


def retrieve_context(
    query: str,
    intent: AudioIntent | None = None,
    entities: Iterable[PublicEntity] | None = None,
    limit: int | None = None,
) -> list[RetrievedDocument]:
    """Escolhe banco quando configurado e JSON local como fallback explicito."""

    if not is_database_rag_configured():
        from app.rag.sharepoint import retrieve_sharepoint_context

        return retrieve_sharepoint_context(query, limit=limit)

    return retrieve_database_context(query, intent=intent, entities=entities, limit=limit)


def _expand_query_terms(query: str, intent: AudioIntent | None) -> set[str]:
    terms = set(_meaningful_tokens(query))
    if not intent:
        return terms

    terms.update(_meaningful_tokens(intent.macro))
    terms.update(_meaningful_tokens(intent.specific))
    if intent.specific == "consulta_status_projeto":
        terms.update({"status", "situacao", "andamento"})
    elif intent.specific == "consulta_cronograma_prazo":
        terms.update({"prazo", "cronograma", "periodo", "validade"})
    elif intent.specific == "consulta_riscos_projeto":
        terms.update({"risco", "problema", "falha", "manutencao"})
    return terms


def _entity_terms(entities: Iterable[PublicEntity]) -> set[str]:
    terms: set[str] = set()
    for entity in entities:
        if entity.type not in {"projeto", "linha"} and "projeto" not in entity.types:
            continue
        terms.add(entity.value)
        terms.add(entity.text)
        terms.update(_meaningful_tokens(entity.value))
        terms.update(_meaningful_tokens(entity.text))
    return {term for term in terms if term}


def _row_to_result(row: object) -> RetrievedDocument:
    if isinstance(row, dict):
        value = row.get
    else:
        value = (
            lambda key, default=None: row[_ROW_INDEX[key]]
            if key in _ROW_INDEX
            else default
        )

    source_id = str(value("partner_source_id") or value("extract_id"))
    project_code = value("project_code")
    list_name = str(value("sharepoint_library") or "Banco de conhecimento")
    if project_code:
        list_name = f"{list_name} / {project_code}"

    document = SharePointDocument(
        source_id=source_id,
        title=str(value("artifact_title") or "Fonte sem titulo"),
        list_name=list_name,
        content=str(value("content_text") or ""),
        web_url=str(value("sharepoint_url") or ""),
        last_modified=str(value("last_modified") or ""),
        search_text=str(value("content_text") or ""),
        artifact_id=_optional_str(value("artifact_id")),
        extract_id=_optional_str(value("extract_id")),
        project_id=_optional_str(value("project_id")),
        source_locator=_optional_str(value("source_locator")),
        fallback=False,
    )
    return RetrievedDocument(
        document=document,
        score=round(float(value("score") or 0), 3),
    )


_ROW_INDEX = {
    "extract_id": 0,
    "artifact_id": 1,
    "project_id": 2,
    "partner_source_id": 3,
    "artifact_title": 4,
    "sharepoint_library": 5,
    "sharepoint_url": 6,
    "last_modified": 7,
    "content_text": 8,
    "source_locator": 9,
    "project_code": 10,
    "project_title": 11,
    "score": 12,
}


def _optional_str(value: object) -> str | None:
    return str(value) if value else None
