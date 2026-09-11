"""A conversa do visitante com o agente.

Esta rota faz duas coisas ao mesmo tempo: consulta o modelo RAG e registra a
interação na sala, para que ela apareça no painel ao vivo no mesmo instante.
É o ponto onde os dois assuntos do serviço se encontram.

Enquanto o modelo não existir, a rota responde `503` com o motivo — de
propósito. Devolver texto inventado tornaria impossível distinguir, na
apresentação, o que veio dos documentos do que veio do nada.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException

from app import documents as catalog
from app.config import get_settings
from app.dependencies import get_model, get_store
from app.live.store import LiveStore
from app.model.client import RagModel, RagModelError
from app.schemas import ChatRequest, ChatResponse, ChatSource

router = APIRouter(tags=["chat"])


def _with_download_urls(sources: list[ChatSource]) -> list[ChatSource]:
    """Completa o link de download das fontes que vierem sem ele.

    O modelo pode devolver só o nome do arquivo; quem sabe transformá-lo em
    URL é este serviço, que é quem serve a pasta.
    """

    directory = get_settings().documents_dir
    completed: list[ChatSource] = []
    for source in sources:
        if source.download_url:
            completed.append(source)
            continue
        match = catalog.find_by_name(directory, source.document)
        completed.append(
            source.model_copy(update={"download_url": catalog.download_url(match[0])})
            if match
            else source
        )
    return completed


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    store: LiveStore = Depends(get_store),
    model: RagModel = Depends(get_model),
) -> ChatResponse:
    """Pergunta ao agente, registrando pergunta e resposta na sala."""

    session_id = request.session_id
    if session_id:
        # A pergunta entra na sala antes da chamada ao modelo: quem observa vê
        # a pergunta e o "aguardando resposta…" enquanto o modelo pensa.
        session = await store.append_message(
            session_id, "user", request.message, status="thinking"
        )
        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Sessão não encontrada ou expirada. Entre novamente em "
                "POST /api/live/sessions.",
            )

    started = time.perf_counter()
    try:
        answer = await model.answer(request.message, request.previous_interaction_id)
    except RagModelError as error:
        # A falha não pode deixar a sessão presa em "aguardando resposta…".
        if session_id:
            await store.touch(session_id, "idle")
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error

    latency_ms = int((time.perf_counter() - started) * 1000)

    if session_id:
        await store.append_message(session_id, "assistant", answer.text, status="idle")

    return ChatResponse(
        text=answer.text,
        model=answer.model,
        interaction_id=answer.interaction_id,
        latency_ms=latency_ms,
        sources=_with_download_urls(answer.sources),
    )
