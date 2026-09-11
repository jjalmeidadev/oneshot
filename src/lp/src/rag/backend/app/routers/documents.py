"""Listagem e download dos documentos-fonte."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app import documents as catalog
from app.config import get_settings
from app.schemas import DocumentInfo, DocumentsResponse

router = APIRouter(prefix="/api/documents", tags=["documentos"])


@router.get("", response_model=DocumentsResponse)
def list_documents() -> DocumentsResponse:
    """O que hoje existe em `lp/src/rag/documentsRAG`.

    A pasta ainda está vazia: a lista vem vazia até os documentos da sprint
    serem colocados lá, e passa a se preencher sozinha depois — não há
    cadastro a fazer.
    """

    directory = get_settings().documents_dir
    return DocumentsResponse(
        documents=[
            DocumentInfo(
                id=doc_id,
                name=path.name,
                size_bytes=path.stat().st_size,
                download_url=catalog.download_url(doc_id),
            )
            for doc_id, path in catalog.iter_documents(directory)
        ]
    )


@router.get("/{doc_id}/download")
def download_document(doc_id: str) -> FileResponse:
    """Entrega o arquivo original da fonte."""

    path = catalog.resolve(get_settings().documents_dir, doc_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return FileResponse(path, filename=path.name)
