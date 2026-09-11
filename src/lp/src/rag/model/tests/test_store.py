"""O índice de vetores: busca, ordenação e ida e volta ao disco."""

from __future__ import annotations

import numpy as np
import pytest
from helpers import indice_de_teste, trecho

from model.store import IndexNotBuilt, VectorIndex


def test_a_busca_devolve_o_mais_proximo_primeiro():
    resultados = indice_de_teste().search([0.9, 0.4, 0.0], top_k=3)

    assert [r.chunk.section for r in resultados] == ["Riscos", "Cronograma", "TAP"]
    assert resultados[0].score > resultados[1].score > resultados[2].score


def test_top_k_limita_o_retorno():
    assert len(indice_de_teste().search([1, 1, 1], top_k=2)) == 2


def test_pontuacao_baixa_e_cortada():
    # Só o primeiro passa do piso; os outros dois são ruído.
    resultados = indice_de_teste().search([1.0, 0.1, 0.1], top_k=3, min_score=0.5)
    assert [r.chunk.section for r in resultados] == ["Riscos"]


def test_vetor_nulo_nao_recupera_nada():
    assert indice_de_teste().search([0, 0, 0], top_k=3) == []


def test_vetores_sao_normalizados_na_construcao():
    indice = VectorIndex(
        chunks=[trecho("a", "Riscos")],
        vectors=np.array([[3, 4, 0]], dtype=np.float32),
        meta={},
    )
    assert np.isclose(np.linalg.norm(indice.vectors[0]), 1.0)


def test_ida_e_volta_ao_disco_preserva_tudo(tmp_path):
    original = indice_de_teste()
    original.save(tmp_path)
    lido = VectorIndex.load(tmp_path)

    assert lido.size == original.size
    assert lido.fingerprint == "abc123"
    assert [c.section for c in lido.chunks] == [c.section for c in original.chunks]
    # `embed_text` não é gravado; ele é remontado na leitura.
    assert lido.chunks[0].embed_text == original.chunks[0].embed_text
    assert np.allclose(lido.vectors, original.vectors)


def test_indice_inexistente_diz_o_que_fazer(tmp_path):
    with pytest.raises(IndexNotBuilt) as erro:
        VectorIndex.load(tmp_path)
    assert "python -m model.index" in str(erro.value)


def test_trechos_e_vetores_em_numeros_diferentes_e_erro():
    with pytest.raises(ValueError):
        VectorIndex(
            chunks=[trecho("a", "Riscos")],
            vectors=np.array([[1, 0], [0, 1]], dtype=np.float32),
            meta={},
        )
