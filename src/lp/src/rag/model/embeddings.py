"""Cliente de embeddings do Gemini, feito para trabalho em lote.

Vetorizar quinhentos trechos não é uma chamada repetida quinhentas vezes: é um
lote longo contra um serviço com limite de taxa, onde a pergunta certa não é
"como não tomar 429?" e sim "o que acontece quando eu tomar?".

Três respostas moram aqui:

* **Cache em disco.** Cada trecho vetorizado é guardado, indexado por um resumo
  do próprio texto. Uma execução interrompida no meio não joga fora o que já
  fez, e a reindexação de hoje à noite só paga pelos trechos que realmente
  mudaram — o resto vem do disco, de graça.
* **Ritmo controlado.** As chamadas saem espaçadas por um intervalo mínimo, em
  vez de todas de uma vez.
* **Freio adaptativo.** Cada 429 desacelera o lote inteiro e respeita o tempo
  de espera que a própria API sugere. O trabalho fica mais lento em vez de
  falhar, que é o comportamento certo para um lote.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
import re
import time
from pathlib import Path
from typing import Any, Callable, Sequence

import httpx
import numpy as np

from model.config import ModelSettings

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"

RETRYABLE = frozenset({408, 429, 500, 502, 503, 504})
MAX_RETRIES = 8
#: Teto para o intervalo entre chamadas, quando o freio adaptativo aperta.
MAX_INTERVAL_SECONDS = 6.0

CACHE_VECTORS = "embedding-cache.npz"
CACHE_KEYS = "embedding-cache.json"


class EmbeddingError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


# --- Leitura da resposta --------------------------------------------------


def _extract_values(body: dict[str, Any]) -> list[float]:
    """Aceita as duas formas de resposta que a API já usou."""

    if isinstance(body.get("embedding"), dict):
        valores = body["embedding"].get("values")
        if valores:
            return [float(v) for v in valores]

    embeddings = body.get("embeddings")
    if isinstance(embeddings, list) and embeddings:
        primeiro = embeddings[0]
        valores = primeiro.get("values") if isinstance(primeiro, dict) else None
        if valores:
            return [float(v) for v in valores]

    raise EmbeddingError("A resposta de embedding não trouxe vetor algum.")


def _retry_delay(response: httpx.Response) -> float | None:
    """Quanto a própria API pediu para esperar, quando ela diz.

    O 429 do Google costuma trazer um `RetryInfo` com `retryDelay: "31s"`.
    Obedecer é melhor do que adivinhar: espera-se o necessário, e não mais.
    """

    cabecalho = response.headers.get("retry-after")
    if cabecalho:
        try:
            return float(cabecalho)
        except ValueError:
            pass

    try:
        detalhes = response.json().get("error", {}).get("details", [])
    except ValueError:
        return None

    for detalhe in detalhes:
        bruto = detalhe.get("retryDelay") if isinstance(detalhe, dict) else None
        if isinstance(bruto, str):
            achado = re.match(r"^([\d.]+)s?$", bruto.strip())
            if achado:
                return float(achado.group(1))
    return None


# --- Ritmo ----------------------------------------------------------------


class Throttle:
    """Espaça as chamadas e desacelera o lote inteiro quando toma 429."""

    def __init__(self, requests_per_minute: int) -> None:
        self._interval = 60.0 / max(1, requests_per_minute)
        self._next = 0.0
        self._lock = asyncio.Lock()

    @property
    def interval(self) -> float:
        return self._interval

    async def acquire(self) -> None:
        async with self._lock:
            agora = time.monotonic()
            partida = max(agora, self._next)
            self._next = partida + self._interval
        espera = partida - time.monotonic()
        if espera > 0:
            await asyncio.sleep(espera)

    async def back_off(self, seconds: float) -> None:
        """Segura todos os trabalhadores e aperta o ritmo para o resto do lote."""

        async with self._lock:
            self._interval = min(self._interval * 1.5, MAX_INTERVAL_SECONDS)
            self._next = max(self._next, time.monotonic() + seconds)


# --- Cache em disco -------------------------------------------------------


def _cache_key(text: str, settings: ModelSettings) -> str:
    """Resumo do texto e do modelo: mudou qualquer um, o vetor é outro."""

    assinatura = f"{settings.embedding_model}|{settings.embedding_dimensions}|{text}"
    return hashlib.sha256(assinatura.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """Vetores já calculados, guardados entre execuções."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._keys: list[str] = []
        self._index: dict[str, int] = {}
        self._vectors: list[list[float]] = []
        self._sujo = False
        self._load()

    def _load(self) -> None:
        arquivo_chaves = self._dir / CACHE_KEYS
        arquivo_vetores = self._dir / CACHE_VECTORS
        if not arquivo_chaves.exists() or not arquivo_vetores.exists():
            return
        try:
            self._keys = json.loads(arquivo_chaves.read_text(encoding="utf-8"))
            with np.load(arquivo_vetores) as dados:
                matriz = dados["vectors"]
            if len(self._keys) != matriz.shape[0]:
                # Cache inconsistente é cache descartável: ele é só uma
                # economia, nunca uma fonte de verdade.
                self._keys, self._vectors = [], []
                return
            self._vectors = [linha.tolist() for linha in matriz]
            self._index = {chave: i for i, chave in enumerate(self._keys)}
        except Exception:  # noqa: BLE001
            self._keys, self._vectors, self._index = [], [], {}

    def get(self, key: str) -> list[float] | None:
        posicao = self._index.get(key)
        return self._vectors[posicao] if posicao is not None else None

    def put(self, key: str, vector: list[float]) -> None:
        if key in self._index:
            return
        self._index[key] = len(self._keys)
        self._keys.append(key)
        self._vectors.append(vector)
        self._sujo = True

    def flush(self) -> None:
        if not self._sujo or not self._keys:
            return
        self._dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            self._dir / CACHE_VECTORS, vectors=np.array(self._vectors, dtype=np.float32)
        )
        (self._dir / CACHE_KEYS).write_text(
            json.dumps(self._keys), encoding="utf-8"
        )
        self._sujo = False

    def __len__(self) -> int:
        return len(self._keys)


# --- Chamada --------------------------------------------------------------


async def embed_one(
    client: httpx.AsyncClient,
    text: str,
    settings: ModelSettings,
    throttle: Throttle | None = None,
) -> list[float]:
    url = f"{GEMINI_BASE}/models/{settings.embedding_model}:embedContent"
    payload = {
        "content": {"parts": [{"text": text}]},
        "output_dimensionality": settings.embedding_dimensions,
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.require_api_key(),
    }

    ultima: Exception | None = None
    for tentativa in range(MAX_RETRIES):
        if throttle is not None:
            await throttle.acquire()

        try:
            resposta = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as erro:
            ultima = EmbeddingError(f"Falha de rede ao vetorizar: {erro}")
            espera = (2**tentativa) + random.random()
        else:
            if resposta.status_code < 400:
                return _extract_values(resposta.json())

            if resposta.status_code not in RETRYABLE:
                raise EmbeddingError(
                    f"O serviço de embedding respondeu {resposta.status_code}: "
                    f"{resposta.text[:200]}",
                    status_code=resposta.status_code,
                )

            sugerida = _retry_delay(resposta)
            espera = sugerida if sugerida is not None else (2**tentativa) + random.random()
            ultima = EmbeddingError(
                f"O serviço de embedding respondeu {resposta.status_code}.",
                status_code=resposta.status_code,
            )
            if resposta.status_code == 429 and throttle is not None:
                # Não adianta só este trabalhador esperar: o limite é da conta,
                # então o lote inteiro desacelera.
                await throttle.back_off(espera)

        await asyncio.sleep(min(espera, 60.0))

    raise ultima or EmbeddingError("Não foi possível vetorizar o texto.")


async def embed_texts(
    texts: Sequence[str],
    settings: ModelSettings,
    progress: Callable[[int, int], None] | None = None,
    cache: EmbeddingCache | None = None,
) -> list[list[float]]:
    """Vetoriza uma lista de textos, preservando a ordem.

    Com `cache`, o que já foi calculado não é pedido de novo — e o que for
    calculado agora fica guardado, mesmo se a execução falhar no meio.
    """

    resultados: list[list[float] | None] = [None] * len(texts)
    pendentes: list[int] = []

    for i, texto in enumerate(texts):
        guardado = cache.get(_cache_key(texto, settings)) if cache else None
        if guardado is not None:
            resultados[i] = guardado
        else:
            pendentes.append(i)

    ja_prontos = len(texts) - len(pendentes)
    if progress is not None and ja_prontos:
        progress(ja_prontos, len(texts))

    if pendentes:
        throttle = Throttle(settings.embedding_requests_per_minute)
        limite = asyncio.Semaphore(max(1, settings.embedding_concurrency))
        feitos = ja_prontos
        desde_o_ultimo_flush = 0

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:

            async def trabalhar(indice: int) -> None:
                nonlocal feitos, desde_o_ultimo_flush
                async with limite:
                    vetor = await embed_one(client, texts[indice], settings, throttle)
                resultados[indice] = vetor
                if cache is not None:
                    cache.put(_cache_key(texts[indice], settings), vetor)
                    desde_o_ultimo_flush += 1
                    # Gravar de tempos em tempos é o que transforma uma queda
                    # no meio em "continua de onde parou".
                    if desde_o_ultimo_flush >= 25:
                        cache.flush()
                        desde_o_ultimo_flush = 0
                feitos += 1
                if progress is not None:
                    progress(feitos, len(texts))

            try:
                await asyncio.gather(*(trabalhar(i) for i in pendentes))
            finally:
                if cache is not None:
                    cache.flush()

    faltando = [i for i, v in enumerate(resultados) if v is None]
    if faltando:
        raise EmbeddingError(f"{len(faltando)} trechos não foram vetorizados.")
    return [v for v in resultados if v is not None]
