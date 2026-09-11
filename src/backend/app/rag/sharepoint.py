import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data" / "sharepoint"
DEFAULT_RESULT_LIMIT = 3

_STOP_WORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "esta",
    "este",
    "eu",
    "o",
    "os",
    "para",
    "por",
    "qual",
    "que",
    "se",
    "um",
    "uma",
}


@dataclass(frozen=True)
class SharePointDocument:
    source_id: str
    title: str
    list_name: str
    content: str
    web_url: str
    last_modified: str
    search_text: str
    artifact_id: str | None = None
    extract_id: str | None = None
    project_id: str | None = None
    source_locator: str | None = None
    fallback: bool = True


@dataclass(frozen=True)
class RetrievedDocument:
    document: SharePointDocument
    score: float


def load_sharepoint_documents(
    data_dir: Path | None = None,
) -> list[SharePointDocument]:
    directory = data_dir or _configured_data_dir()
    documents: list[SharePointDocument] = []

    if not directory.exists():
        return documents

    for file_path in sorted(directory.glob("*.json")):
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        list_data = payload.get("list", {})
        list_id = str(list_data.get("id") or file_path.stem)
        list_name = str(list_data.get("displayName") or file_path.stem)

        for item in payload.get("value", []):
            fields = item.get("fields", {})
            item_id = str(item.get("id") or fields.get("id") or "sem-id")
            title = str(fields.get("Title") or f"Item {item_id}")
            content = str(
                fields.get("Conteudo")
                or fields.get("Descricao")
                or fields.get("Resumo")
                or ""
            )
            searchable_values = [
                str(value)
                for value in fields.values()
                if isinstance(value, (str, int, float))
            ]
            documents.append(
                SharePointDocument(
                    source_id=f"{list_id}:{item_id}",
                    title=title,
                    list_name=list_name,
                    content=content,
                    web_url=str(item.get("webUrl") or ""),
                    last_modified=str(item.get("lastModifiedDateTime") or ""),
                    search_text=" ".join(searchable_values),
                )
            )

    return documents


def retrieve_sharepoint_context(
    query: str,
    documents: list[SharePointDocument] | None = None,
    limit: int | None = None,
) -> list[RetrievedDocument]:
    query_tokens = _meaningful_tokens(query)
    if not query_tokens:
        return []

    candidates = documents if documents is not None else load_sharepoint_documents()
    scored: list[RetrievedDocument] = []

    for document in candidates:
        normalized_text = _normalize(document.search_text)
        document_tokens = set(normalized_text.split())
        matched_tokens = query_tokens & document_tokens
        if not matched_tokens:
            continue

        title_tokens = set(_normalize(document.title).split())
        title_matches = query_tokens & title_tokens
        if len(query_tokens) > 1 and len(matched_tokens) < 2 and not title_matches:
            continue

        coverage = len(matched_tokens) / len(query_tokens)
        score = len(matched_tokens) + (2 * len(title_matches)) + coverage
        scored.append(RetrievedDocument(document=document, score=round(score, 3)))

    result_limit = limit if limit is not None else _configured_result_limit()
    return sorted(
        scored,
        key=lambda result: (-result.score, result.document.source_id),
    )[:result_limit]


def build_rag_input(message: str, results: list[RetrievedDocument]) -> str:
    if not results:
        return message

    source_blocks = []
    for index, result in enumerate(results, start=1):
        document = result.document
        source_blocks.append(
            "\n".join(
                (
                    f"[Fonte {index}] {document.title}",
                    f"Lista: {document.list_name}",
                    f"Atualizado em: {document.last_modified}",
                    f"Conteudo: {document.content}",
                )
            )
        )

    context = "\n\n".join(source_blocks)
    return (
        "Voce e um assistente do Metro em um ambiente de demonstracao. "
        "Os trechos abaixo vieram de listas simuladas do SharePoint e sao "
        "dados ficticios para o MVP. Use-os quando forem pertinentes, cite "
        "as fontes no formato [Fonte N] e informe quando o contexto nao for "
        "suficiente. Nao apresente esses dados como informacao operacional real.\n\n"
        f"Contexto recuperado:\n{context}\n\n"
        f"Pergunta do usuario: {message}"
    )


def _configured_data_dir() -> Path:
    configured = os.getenv("SHAREPOINT_MOCK_DATA_DIR", "").strip()
    return Path(configured) if configured else DEFAULT_DATA_DIR


def _configured_result_limit() -> int:
    raw_value = os.getenv("RAG_MAX_SOURCES", str(DEFAULT_RESULT_LIMIT))
    try:
        return min(max(int(raw_value), 1), 8)
    except ValueError:
        return DEFAULT_RESULT_LIMIT


def _meaningful_tokens(value: str) -> set[str]:
    return {
        token
        for token in _normalize(value).split()
        if len(token) >= 3 and token not in _STOP_WORDS
    }


def _normalize(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.decode().lower()).strip()
