"""Distribuição das mudanças da sala pelos WebSockets abertos.

O hub não conhece o store: ele recebe a sala já pronta e a empurra para quem
estiver ouvindo. Quem observa (`/ws/live`) nunca escreve — o canal é de mão
única, o que dispensa qualquer tratamento de entrada.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import WebSocket

from app.schemas import LiveEvent, LiveSession

logger = logging.getLogger(__name__)


class LiveHub:
    """Conjunto de observadores conectados."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    @property
    def client_count(self) -> int:
        return len(self._clients)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)

    async def send(
        self,
        websocket: WebSocket,
        sessions: list[LiveSession],
        event_type: str = "sessions",
    ) -> None:
        event = LiveEvent(type=event_type, sessions=sessions)  # type: ignore[arg-type]
        await websocket.send_json(event.model_dump(by_alias=True))

    async def broadcast(self, sessions: list[LiveSession]) -> None:
        """Envia a sala para todos, descartando as conexões que morreram.

        Uma conexão que caiu não pode impedir as outras de receber, então cada
        envio é isolado e a falha só custa aquele cliente.
        """

        async with self._lock:
            clients = list(self._clients)

        if not clients:
            return

        payload = LiveEvent(type="sessions", sessions=sessions).model_dump(by_alias=True)
        dead: list[WebSocket] = []
        for client in clients:
            try:
                await client.send_json(payload)
            except Exception:  # noqa: BLE001 - qualquer falha aqui é desconexão
                dead.append(client)

        if dead:
            async with self._lock:
                for client in dead:
                    self._clients.discard(client)
            logger.info("Removidos %d observadores desconectados.", len(dead))
