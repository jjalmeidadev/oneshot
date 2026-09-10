"""Cliente de embeddings do Gemini.

Uma chamada por trecho, com concorrência limitada e repetição em caso de 429 —
que é o erro que aparece quando se tenta vetorizar quinhentos trechos de uma
vez. O formato da resposta é tratado nas duas formas que a API já usou
(`embedding` e `embeddings`), porque a diferença entre elas é invisível até
quebrar em produção.
"""

from __future__ import annotations

import asyncio
import random
from typing import Any, Callable, Sequence

import httpx

from model.config import ModelSettings

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"

RETRYABLE = frozenset({408, 429, 500, 502, 503, 504})
MAX_RETRIES = 4


class EmbeddingError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def _extract_values(body: dict[str, Any]) -> list[float]:
    """Aceita as duas formas de resposta da API."""

    if isinstance(body.get("embedding"), dict):
        valores = body["embedding"].get("values")
        if valores:
            return [float(v) for v in valores]

    embeddings = body.get("embeddings")
    if isinstance(embeddings, list) and embeddings:
        valores = embeddings[0].get("values") if isinstance(embeddings[0], dict) else None
        if valores:
            return [float(v) for v in valores]

    raise EmbeddingError("A resposta de embedding não trouxe vetor algum.")


async def embed_one(
    client: httpx.AsyncClient, text: str, settings: ModelSettings
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
        try:
            resposta = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as erro:
            ultima = EmbeddingError(f"Falha de rede ao vetorizar: {erro}")
        else:
            if resposta.status_code < 400:
                return _extract_values(resposta.json())
            if resposta.status_code not in RETRYABLE:
                raise EmbeddingError(
                    f"O serviço de embedding respondeu {resposta.status_code}: "
                    f"{resposta.text[:200]}",
                    status_code=resposta.status_code,
                )
            ultima = EmbeddingError(
                f"O serviço de embedding respondeu {resposta.status_code}.",
                status_code=resposta.status_code,
            )

        # Espera crescente com ruído: quinhentas repetições sincronizadas
        # bateriam no limite de novo, todas ao mesmo tempo.
        await asyncio.sleep((2**tentativa) + random.random())

    raise ultima or EmbeddingError("Não foi possível vetorizar o texto.")


async def embed_texts(
    texts: Sequence[str],
    settings: ModelSettings,
    progress: Callable[[int, int], None] | None = None,
) -> list[list[float]]:
    """Vetoriza uma lista de textos, preservando a ordem."""

    resultados: list[list[float] | None] = [None] * len(texts)
    limite = asyncio.Semaphore(max(1, settings.embedding_concurrency))
    concluidos = 0

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:

        async def trabalhar(indice: int, texto: str) -> None:
            nonlocal concluidos
            async with limite:
                resultados[indice] = await embed_one(client, texto, settings)
                concluidos += 1
                if progress is not None:
                    progress(concluidos, len(texts))

        await asyncio.gather(
            *(trabalhar(i, texto) for i, texto in enumerate(texts))
        )

    faltando = [i for i, v in enumerate(resultados) if v is None]
    if faltando:
        raise EmbeddingError(f"{len(faltando)} trechos não foram vetorizados.")
    return [v for v in resultados if v is not None]
