"""A sala: quem está conversando com o agente e o que já foi dito.

Guardado apenas em memória, de propósito. O painel ao vivo é uma vitrine de
apresentação — o que importa é o que está acontecendo agora, e reiniciar o
servidor limpar a sala é comportamento aceitável nesta etapa. Toda a escrita
passa por esta classe, atrás de um `asyncio.Lock`, e cada mudança avisa os
inscritos (hoje, o hub de WebSocket) com a sala inteira já pronta para enviar.

Trocar isto por um banco depois é substituir esta classe: as rotas só
conhecem os métodos públicos abaixo.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Iterable

from app.config import Settings
from app.schemas import LiveMessage, LiveSession, Role, SessionStatus

#: Mesma paleta usada pelo painel de presença da LP, para que a cor do ponto
#: seja a mesma que o visitante vê.
COLORS = ("#818cf8", "#34d399", "#fbbf24", "#f472b6", "#38bdf8")

Listener = Callable[[list[LiveSession]], Awaitable[None]]


def now_ms() -> int:
    """Epoch em milissegundos — a mesma unidade que `Date.now()`."""

    return int(time.time() * 1000)


class SessionLimitReached(RuntimeError):
    """A sala está cheia."""


class LiveStore:
    """Estado da sala, com acesso serializado."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._sessions: dict[str, LiveSession] = {}
        self._listeners: list[Listener] = []
        self._lock = asyncio.Lock()
        self._joined = 0

    # --- Inscrição em mudanças -------------------------------------------

    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    async def _notify(self, sessions: list[LiveSession]) -> None:
        """Avisa os inscritos fora do lock, para não segurar a sala."""

        for listener in list(self._listeners):
            await listener(sessions)

    # --- Leitura ----------------------------------------------------------

    async def snapshot(self) -> list[LiveSession]:
        async with self._lock:
            return self._snapshot_locked()

    def _snapshot_locked(self) -> list[LiveSession]:
        # Cópia profunda: quem recebe a lista pode serializá-la com calma sem
        # correr o risco de uma escrita concorrente mudar o objeto no meio.
        return [session.model_copy(deep=True) for session in self._sessions.values()]

    async def get(self, session_id: str) -> LiveSession | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            return session.model_copy(deep=True) if session else None

    # --- Escrita ----------------------------------------------------------

    async def join(self, name: str | None = None) -> LiveSession:
        """Coloca um visitante na sala e devolve a sessão criada."""

        async with self._lock:
            if len(self._sessions) >= self._settings.max_sessions:
                raise SessionLimitReached(
                    f"A sala está cheia ({self._settings.max_sessions} sessões)."
                )

            self._joined += 1
            session = LiveSession(
                id=uuid.uuid4().hex[:12],
                name=(name or "").strip() or f"Convidado {self._joined}",
                color=COLORS[(self._joined - 1) % len(COLORS)],
                status="idle",
                lastSeen=now_ms(),
                messages=[],
            )
            self._sessions[session.id] = session
            snapshot = self._snapshot_locked()

        await self._notify(snapshot)
        return session.model_copy(deep=True)

    async def leave(self, session_id: str) -> bool:
        async with self._lock:
            removed = self._sessions.pop(session_id, None)
            if removed is None:
                return False
            snapshot = self._snapshot_locked()

        await self._notify(snapshot)
        return True

    async def touch(
        self, session_id: str, status: SessionStatus | None = None
    ) -> LiveSession | None:
        """Sinal de vida, opcionalmente mudando o estado exibido."""

        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            session.last_seen = now_ms()
            if status is not None:
                session.status = status
            result = session.model_copy(deep=True)
            snapshot = self._snapshot_locked()

        await self._notify(snapshot)
        return result

    async def append_message(
        self,
        session_id: str,
        role: Role,
        content: str,
        status: SessionStatus | None = None,
    ) -> LiveSession | None:
        """Registra uma fala na conversa e reflete no painel."""

        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None

            now = now_ms()
            session.messages.append(
                LiveMessage(
                    id=f"{session_id}-{role[0]}-{uuid.uuid4().hex[:8]}",
                    role=role,
                    content=content,
                    at=now,
                )
            )
            # Conversa longa não pode virar vazamento de memória: só a cauda
            # interessa a quem está observando.
            excess = len(session.messages) - self._settings.max_messages_per_session
            if excess > 0:
                del session.messages[:excess]

            session.last_seen = now
            if status is not None:
                session.status = status
            result = session.model_copy(deep=True)
            snapshot = self._snapshot_locked()

        await self._notify(snapshot)
        return result

    async def sweep(self) -> list[str]:
        """Remove as sessões sem sinal de vida e devolve os ids removidos."""

        limit = self._settings.session_ttl_seconds * 1000
        async with self._lock:
            cutoff = now_ms() - limit
            expired = [
                session_id
                for session_id, session in self._sessions.items()
                if session.last_seen < cutoff
            ]
            for session_id in expired:
                del self._sessions[session_id]
            if not expired:
                return []
            snapshot = self._snapshot_locked()

        await self._notify(snapshot)
        return expired

    async def reset(self, sessions: Iterable[LiveSession] = ()) -> None:
        """Reinicia a sala. Existe para os testes, não para as rotas."""

        async with self._lock:
            self._sessions = {session.id: session for session in sessions}
            self._joined = len(self._sessions)
            snapshot = self._snapshot_locked()

        await self._notify(snapshot)
