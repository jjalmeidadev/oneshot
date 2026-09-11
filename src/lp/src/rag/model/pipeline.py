"""O caminho completo: pergunta → trechos → resposta com fontes.

As dependências externas (vetorizar e gerar) entram pelo construtor. É o que
permite testar recuperação, ordenação e montagem das fontes sem tocar na rede —
e sem gastar cota do Gemini a cada `pytest`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Sequence

from model.config import ModelSettings, get_model_settings
from model.embeddings import embed_texts
from model.generator import GenerationResult, generate
from model.store import SearchHit, VectorIndex

Embedder = Callable[[Sequence[str], ModelSettings], Awaitable[list[list[float]]]]
Generator = Callable[
    [str, list[SearchHit], ModelSettings, str | None], Awaitable[GenerationResult]
]


@dataclass
class PipelineSource:
    """Uma fonte, no vocabulário que o backend já espera."""

    id: str
    title: str
    #: Nome do arquivo. É por ele que o backend descobre o link de download.
    document: str
    anchor: str
    excerpt: str
    score: float


@dataclass
class PipelineAnswer:
    text: str
    model: str
    interaction_id: str | None = None
    sources: list[PipelineSource] = field(default_factory=list)
    retrieval_ms: int = 0
    generation_ms: int = 0


async def _default_embed(
    texts: Sequence[str], settings: ModelSettings
) -> list[list[float]]:
    return await embed_texts(texts, settings)


async def _default_generate(
    question: str,
    hits: list[SearchHit],
    settings: ModelSettings,
    previous_interaction_id: str | None,
) -> GenerationResult:
    return await generate(question, hits, settings, previous_interaction_id)


class RagPipeline:
    """Junta índice, recuperação e geração."""

    def __init__(
        self,
        settings: ModelSettings | None = None,
        index: VectorIndex | None = None,
        embed: Embedder | None = None,
        generator: Generator | None = None,
    ) -> None:
        self.settings = settings or get_model_settings()
        self._index = index
        self._embed = embed or _default_embed
        self._generate = generator or _default_generate

    @property
    def index(self) -> VectorIndex:
        """Carrega o índice na primeira necessidade e o mantém em memória."""

        if self._index is None:
            self._index = VectorIndex.load(self.settings.artifacts_dir)
        return self._index

    async def answer(
        self, question: str, previous_interaction_id: str | None = None
    ) -> PipelineAnswer:
        comeco = time.perf_counter()
        vetores = await self._embed([question], self.settings)
        hits = self.index.search(
            vetores[0], top_k=self.settings.top_k, min_score=self.settings.min_score
        )
        retrieval_ms = int((time.perf_counter() - comeco) * 1000)

        comeco = time.perf_counter()
        resultado = await self._generate(
            question, hits, self.settings, previous_interaction_id
        )
        generation_ms = int((time.perf_counter() - comeco) * 1000)

        return PipelineAnswer(
            text=resultado.text,
            model=resultado.model,
            interaction_id=resultado.interaction_id,
            sources=_build_sources(hits),
            retrieval_ms=retrieval_ms,
            generation_ms=generation_ms,
        )


def _build_sources(hits: list[SearchHit]) -> list[PipelineSource]:
    """Converte os trechos recuperados em fontes.

    A ordem e a quantidade acompanham exatamente os trechos que foram para o
    prompt — sem remover repetidos. É isso que faz `[Fonte 3]` no texto da
    resposta corresponder à terceira fonte da lista; deduplicar aqui
    desalinharia a citação do documento.
    """

    fontes: list[PipelineSource] = []
    for hit in hits:
        trecho = hit.chunk
        resumo = trecho.text.strip().replace("\n", " ")
        fontes.append(
            PipelineSource(
                id=trecho.id,
                title=trecho.section or trecho.document,
                document=trecho.document,
                anchor=trecho.anchor,
                excerpt=(resumo[:280] + "…") if len(resumo) > 280 else resumo,
                score=round(hit.score, 4),
            )
        )
    return fontes
