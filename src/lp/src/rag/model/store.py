"""O índice de vetores.

Deliberadamente simples: uma matriz em memória e produto escalar. Com pouco
mais de quinhentos trechos, uma busca exaustiva percorre tudo em menos de um
milissegundo — um banco vetorial aqui só acrescentaria um serviço para manter
de pé, um formato para migrar e um modo de falhar a mais.

Os vetores são normalizados na construção, então o cosseno vira produto
escalar e a busca é uma multiplicação de matriz.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from model.corpus import Chunk

VECTORS_FILE = "index.npz"
METADATA_FILE = "index.json"


class IndexNotBuilt(RuntimeError):
    """Ainda não existe índice em disco."""


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


def _normalize(matrix: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(matrix, axis=1, keepdims=True)
    # Um vetor nulo não deve virar divisão por zero; ele simplesmente nunca
    # será recuperado.
    normas[normas == 0] = 1.0
    return matrix / normas


class VectorIndex:
    """Trechos e seus vetores, prontos para busca."""

    def __init__(self, chunks: list[Chunk], vectors: np.ndarray, meta: dict) -> None:
        if len(chunks) != vectors.shape[0]:
            raise ValueError(
                f"{len(chunks)} trechos para {vectors.shape[0]} vetores — "
                "o índice está inconsistente."
            )
        self.chunks = chunks
        self.vectors = _normalize(vectors.astype(np.float32))
        self.meta = meta

    @property
    def size(self) -> int:
        return len(self.chunks)

    @property
    def fingerprint(self) -> str:
        return str(self.meta.get("fingerprint", ""))

    # --- Busca ------------------------------------------------------------

    def search(
        self, query_vector: list[float], top_k: int = 5, min_score: float = 0.0
    ) -> list[SearchHit]:
        if self.size == 0:
            return []

        consulta = np.asarray(query_vector, dtype=np.float32)
        norma = float(np.linalg.norm(consulta))
        if norma == 0:
            return []
        consulta = consulta / norma

        pontuacoes = self.vectors @ consulta
        # `argpartition` evita ordenar quinhentos itens para pegar cinco.
        quantos = min(top_k, self.size)
        candidatos = np.argpartition(-pontuacoes, quantos - 1)[:quantos]
        candidatos = candidatos[np.argsort(-pontuacoes[candidatos])]

        return [
            SearchHit(chunk=self.chunks[int(i)], score=float(pontuacoes[int(i)]))
            for i in candidatos
            if float(pontuacoes[int(i)]) >= min_score
        ]

    # --- Disco ------------------------------------------------------------

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(directory / VECTORS_FILE, vectors=self.vectors)

        # `embed_text` não é gravado: ele é documento + seção + texto, e
        # remontá-lo na leitura custa nada e evita duplicar o corpus no JSON.
        (directory / METADATA_FILE).write_text(
            json.dumps(
                {
                    "meta": {**self.meta, "saved_at": datetime.now(timezone.utc).isoformat()},
                    "chunks": [
                        {
                            "id": c.id,
                            "document": c.document,
                            "relative_path": c.relative_path,
                            "section": c.section,
                            "anchor": c.anchor,
                            "text": c.text,
                            "order": c.order,
                        }
                        for c in self.chunks
                    ],
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, directory: Path) -> "VectorIndex":
        vetores = directory / VECTORS_FILE
        metadados = directory / METADATA_FILE
        if not vetores.exists() or not metadados.exists():
            raise IndexNotBuilt(
                f"Não há índice em {directory}. Rode `python -m model.index` "
                "para construí-lo a partir da documentação."
            )

        dados = json.loads(metadados.read_text(encoding="utf-8"))
        chunks = [
            Chunk(
                id=c["id"],
                document=c["document"],
                relative_path=c["relative_path"],
                section=c["section"],
                anchor=c["anchor"],
                text=c["text"],
                embed_text=f"{c['document']} — {c['section']}\n\n{c['text']}",
                order=c["order"],
            )
            for c in dados["chunks"]
        ]
        with np.load(vetores) as arquivo:
            matriz = arquivo["vectors"]

        return cls(chunks=chunks, vectors=matriz, meta=dados.get("meta", {}))
