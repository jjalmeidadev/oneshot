"""Catálogo dos documentos que sustentam as respostas.

A pasta é `lp/src/rag/documentsRAG` — a mesma que será vetorizada pelo modelo.
Aqui ela cumpre o outro papel: entregar o arquivo original para download,
porque a exigência do produto é que toda resposta indique a fonte e a fonte
seja abrível.

Cada arquivo recebe um identificador derivado do caminho relativo. Isso evita
que nome de arquivo com espaço, acento ou barra entre na URL, e — mais
importante — torna impossível pedir um caminho arbitrário: o identificador não
é um caminho, e só resolve para arquivos que este módulo listou.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

#: Arquivos que não são fonte e não devem aparecer no catálogo.
IGNORED_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db"}


def document_id(relative_path: str) -> str:
    """Identificador estável e opaco para um caminho relativo."""

    return hashlib.sha1(relative_path.encode("utf-8")).hexdigest()[:12]


def download_url(doc_id: str) -> str:
    return f"/api/documents/{doc_id}/download"


def iter_documents(directory: Path) -> list[tuple[str, Path]]:
    """Todos os arquivos da pasta, em ordem estável, como `(id, caminho)`."""

    if not directory.is_dir():
        return []

    found: list[tuple[str, Path]] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IGNORED_NAMES or path.name.startswith("."):
            continue
        relative = path.relative_to(directory).as_posix()
        found.append((document_id(relative), path))
    return found


def resolve(directory: Path, doc_id: str) -> Path | None:
    """Caminho do documento com esse identificador, se ele existir."""

    for candidate_id, path in iter_documents(directory):
        if candidate_id == doc_id:
            return path
    return None


def find_by_name(directory: Path, name: str) -> tuple[str, Path] | None:
    """Documento cujo nome de arquivo bate com `name`.

    Serve para completar as fontes devolvidas pelo modelo: se ele indicar
    apenas `TAP — Portfólio XPTO.pdf`, o backend descobre sozinho o link de
    download correspondente.
    """

    target = name.strip().lower()
    for doc_id, path in iter_documents(directory):
        if path.name.lower() == target:
            return doc_id, path
    return None
