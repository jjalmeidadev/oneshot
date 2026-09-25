"""Cassetes de transcricao em memoria, limitados por TTL e capacidade.

Nao guarda audio, credenciais ou erros. O cache e local ao processo; reiniciar
o worker descarta os cassetes. Locks protegem apenas operacoes em memoria.
"""

from __future__ import annotations

import asyncio
from collections import Counter, OrderedDict
from concurrent.futures import Future
from threading import RLock
from time import monotonic
from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


class ResponseCache(Generic[T]):
    def __init__(self, *, ttl_seconds=300, max_entries=256, clock=monotonic):
        if ttl_seconds <= 0 or max_entries < 1:
            raise ValueError("TTL e capacidade devem ser positivos.")
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.clock = clock
        self._entries = OrderedDict()
        self._pending = {}
        self._lock = RLock()
        self._generation = 0
        self._metrics = Counter()

    def metrics(self) -> dict[str, int]:
        with self._lock:
            return {name: self._metrics[name] for name in (
                "hit", "miss", "record", "expired", "invalidation",
                "eviction", "provider_call", "provider_error", "coalesced",
            )}

    def invalidate(self) -> int:
        """Descarta tudo; chamadas em andamento nao repovoam esta geracao."""
        with self._lock:
            count = len(self._entries)
            self._entries.clear()
            self._pending.clear()
            self._generation += 1
            self._metrics["invalidation"] += 1
            return count

    async def get_or_record(self, key: str, provider: Callable[[], Awaitable[T]]) -> T:
        with self._lock:
            now = self.clock()
            for old_key, (deadline, _) in list(self._entries.items()):
                if deadline <= now:
                    del self._entries[old_key]
                    self._metrics["expired"] += 1
            if key in self._entries:
                self._metrics["hit"] += 1
                self._entries.move_to_end(key)
                return self._entries[key][1]
            generation = self._generation
            pending = self._pending.get(key)
            owner = pending is None
            if owner:
                pending = Future()
                self._pending[key] = pending
                self._metrics["miss"] += 1
                self._metrics["provider_call"] += 1
            else:
                self._metrics["coalesced"] += 1

        if not owner:
            return await asyncio.shield(asyncio.wrap_future(pending))
        try:
            result = await provider()
        except BaseException as error:
            with self._lock:
                self._metrics["provider_error"] += 1
                if self._pending.get(key) is pending:
                    del self._pending[key]
                pending.set_exception(error)
            raise
        with self._lock:
            if generation == self._generation:
                self._entries[key] = (self.clock() + self.ttl_seconds, result)
                self._metrics["record"] += 1
                while len(self._entries) > self.max_entries:
                    self._entries.popitem(last=False)
                    self._metrics["eviction"] += 1
            if self._pending.get(key) is pending:
                del self._pending[key]
            pending.set_result(result)
        return result
