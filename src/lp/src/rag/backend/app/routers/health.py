"""Diagnóstico rápido do serviço."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app import __version__
from app.dependencies import get_hub, get_model, get_store
from app.live.hub import LiveHub
from app.live.store import LiveStore
from app.model.client import RagModel

router = APIRouter(tags=["saúde"])


@router.get("/health")
async def health(
    store: LiveStore = Depends(get_store),
    hub: LiveHub = Depends(get_hub),
    model: RagModel = Depends(get_model),
) -> dict[str, object]:
    """Estado do serviço — útil para conferir se o modelo já está ligado."""

    sessions = await store.snapshot()
    return {
        "status": "ok",
        "version": __version__,
        "model": model.name,
        "live_sessions": len(sessions),
        "observers": hub.client_count,
    }
