"""Peças pequenas compartilhadas pelos testes."""

from __future__ import annotations

import numpy as np

from model.corpus import Chunk
from model.store import VectorIndex


def trecho(identificador: str, secao: str) -> Chunk:
    return Chunk(
        id=identificador,
        document="Projeto.md",
        relative_path="Projeto.md",
        section=secao,
        anchor=secao.lower(),
        text=f"Conteúdo de {secao}.",
        embed_text=f"Projeto.md — {secao}\n\nConteúdo de {secao}.",
        order=0,
    )


def indice_de_teste() -> VectorIndex:
    # Vetores ortogonais: assim dá para escolher exatamente quem deve ganhar.
    return VectorIndex(
        chunks=[trecho("a", "Riscos"), trecho("b", "Cronograma"), trecho("c", "TAP")],
        vectors=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32),
        meta={"fingerprint": "abc123"},
    )
