"""Construção e conferência do índice.

    python -m model.index            constrói o índice a partir da documentação
    python -m model.index --check    diz se a documentação mudou desde então
    python -m model.index --stats    mostra o que há no índice atual

O `--check` é a salvaguarda contra apresentar com índice velho: ele compara a
impressão digital do corpus guardada no índice com a da documentação em disco
e sai com código 1 se elas divergirem.
"""

from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from model.config import ModelSettings, get_model_settings
from model.corpus import build_chunks, fingerprint
from model.embeddings import embed_texts
from model.store import IndexNotBuilt, VectorIndex


def _progresso(feitos: int, total: int) -> None:
    if feitos % 25 == 0 or feitos == total:
        print(f"  vetorizados {feitos}/{total}", flush=True)


def _copiar_para_documentos(documentos, destino: Path) -> int:
    """Copia o corpus indexado para a pasta servida como fonte para download.

    A cópia acontece no momento da indexação, de propósito: garante que o
    arquivo que o usuário baixa é exatamente o que foi vetorizado, e não uma
    versão que mudou depois.
    """

    destino.mkdir(parents=True, exist_ok=True)
    for documento in documentos:
        shutil.copy2(documento.path, destino / documento.name)
    return len(documentos)


async def construir(settings: ModelSettings) -> VectorIndex:
    print(f"Lendo a documentação em {settings.corpus_dir}")
    trechos, documentos, ignorados = build_chunks(
        settings.corpus_dir, settings.max_chunk_chars, settings.chunk_overlap_chars
    )
    if not trechos:
        raise SystemExit("Nenhum trecho encontrado — a pasta da documentação está vazia?")

    print(f"  {len(documentos)} documentos, {len(trechos)} trechos")
    if ignorados:
        print(f"  {len(ignorados)} arquivos ignorados (formato ainda sem carregador):")
        for nome in ignorados[:10]:
            print(f"    - {nome}")

    print(f"Vetorizando com {settings.embedding_model} ({settings.embedding_dimensions}d)")
    vetores = await embed_texts(
        [t.embed_text for t in trechos], settings, progress=_progresso
    )

    indice = VectorIndex(
        chunks=trechos,
        vectors=np.array(vetores, dtype=np.float32),
        meta={
            "embedding_model": settings.embedding_model,
            "dimensions": settings.embedding_dimensions,
            "fingerprint": fingerprint(documentos),
            "built_at": datetime.now(timezone.utc).isoformat(),
            "chunk_count": len(trechos),
            "documents": [d.relative_path for d in documentos],
        },
    )
    indice.save(settings.artifacts_dir)
    print(f"Índice gravado em {settings.artifacts_dir}")

    copiados = _copiar_para_documentos(documentos, settings.documents_dir)
    print(f"{copiados} documentos copiados para {settings.documents_dir} (fontes para download)")
    return indice


def conferir(settings: ModelSettings) -> int:
    """0 se o índice está em dia com a documentação, 1 se não."""

    try:
        indice = VectorIndex.load(settings.artifacts_dir)
    except IndexNotBuilt as erro:
        print(f"✗ {erro}")
        return 1

    _, documentos, _ = build_chunks(settings.corpus_dir)
    atual = fingerprint(documentos)

    if atual == indice.fingerprint:
        print(f"✓ Índice em dia ({indice.size} trechos, impressão {atual}).")
        return 0

    print(
        f"✗ A documentação mudou desde a última indexação.\n"
        f"  índice: {indice.fingerprint}\n"
        f"  agora:  {atual}\n"
        f"  Rode `python -m model.index` antes de apresentar."
    )
    return 1


def estatisticas(settings: ModelSettings) -> int:
    try:
        indice = VectorIndex.load(settings.artifacts_dir)
    except IndexNotBuilt as erro:
        print(f"✗ {erro}")
        return 1

    print(f"Trechos: {indice.size}")
    for chave in ("embedding_model", "dimensions", "fingerprint", "built_at"):
        print(f"{chave}: {indice.meta.get(chave)}")
    print("Documentos:")
    for nome in indice.meta.get("documents", []):
        quantos = sum(1 for c in indice.chunks if c.relative_path == nome)
        print(f"  {nome}: {quantos} trechos")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Índice do modelo RAG do OneShot.")
    parser.add_argument("--check", action="store_true", help="só confere se está em dia")
    parser.add_argument("--stats", action="store_true", help="mostra o índice atual")
    args = parser.parse_args(argv)

    settings = get_model_settings()

    if args.check:
        return conferir(settings)
    if args.stats:
        return estatisticas(settings)

    asyncio.run(construir(settings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
