"""Presença ao vivo: entrada na sala, leitura por polling e canal WebSocket.

Dois públicos distintos passam por aqui:

* o **visitante**, que entra na sala (`POST /api/live/sessions`), dá sinal de
  vida e conversa pelo `/api/chat`;
* o **observador**, que só lê — pelo `GET /api/live/sessions` (o polling que a
  LP já sabia fazer) ou pelo `/ws/live` (atualização no instante da mudança).

Os dois caminhos devolvem exatamente o mesmo objeto de sessão, então o
frontend pode trocar de transporte sem tocar em componente nenhum.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, WebSocket, WebSocketDisconnect

from app.dependencies import get_hub, get_store
from app.live.hub import LiveHub
from app.live.store import LiveStore, SessionLimitReached
from app.schemas import (
    HeartbeatRequest,
    JoinRequest,
    LiveSession,
    LiveSessionsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ao vivo"])


@router.post("/api/live/sessions", response_model=LiveSession, status_code=201)
async def join(
    request: JoinRequest | None = None,
    store: LiveStore = Depends(get_store),
) -> LiveSession:
    """Coloca um visitante na sala e devolve a sessão (guarde o `id`)."""

    try:
        return await store.join(request.name if request else None)
    except SessionLimitReached as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/api/live/sessions", response_model=LiveSessionsResponse)
async def list_sessions(store: LiveStore = Depends(get_store)) -> LiveSessionsResponse:
    """A sala inteira. É o corpo que `useLivePresence` consome no polling."""

    return LiveSessionsResponse(sessions=await store.snapshot())


@router.post("/api/live/sessions/{session_id}/heartbeat", response_model=LiveSession)
async def heartbeat(
    session_id: str,
    request: HeartbeatRequest | None = None,
    store: LiveStore = Depends(get_store),
) -> LiveSession:
    """Sinal de vida. Sem ele, a sessão sai da sala ao fim do TTL."""

    session = await store.touch(session_id, request.status if request else None)
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return session


@router.delete("/api/live/sessions/{session_id}", status_code=204)
async def leave(session_id: str, store: LiveStore = Depends(get_store)) -> Response:
    """Saída explícita — o visitante fechou a aba."""

    await store.leave(session_id)
    return Response(status_code=204)


@router.websocket("/ws/live")
async def live_feed(
    websocket: WebSocket,
    store: LiveStore = Depends(get_store),
    hub: LiveHub = Depends(get_hub),
) -> None:
    """Canal de observação: a sala inteira agora e a cada mudança.

    É de mão única. Nada que o cliente enviar é interpretado — a leitura serve
    só para perceber que a conexão caiu (e para aceitar um ping, se o cliente
    quiser mandar um).
    """

    await hub.connect(websocket)
    try:
        await hub.send(websocket, await store.snapshot(), event_type="snapshot")
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001
        logger.info("Observador desconectado por falha no canal.", exc_info=True)
    finally:
        await hub.disconnect(websocket)
