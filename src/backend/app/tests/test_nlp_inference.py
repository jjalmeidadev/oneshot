"""Inferência do classificador de intenções (Seção 8.10.3 do Projeto.md).

Os testes carregam os artefatos reais — inclusive o encoder BERT, baixado na
primeira execução. São marcados como lentos e compartilham uma única instância.
"""

import csv
import warnings
from pathlib import Path

import numpy as np
import pytest

from app.nlp.inference import (
    LIMITATION_ANSWER,
    UNDEFINED_MACRO,
    ClassificadorDeIntencoes,
    Classificacao,
    classify,
    get_classifier,
)

DATASET = (
    Path(__file__).resolve().parents[3]
    / "notebooks"
    / "artefatos"
    / "dataset_intencoes.csv"
)

# A representacao vencedora combina Word2Vec e BERT, que vivem fora do joblib.
# Sem as dependencias de requirements-pln.txt nao ha o que exercitar.
pytest.importorskip("gensim", reason="instale requirements-pln.txt")
pytest.importorskip("onnxruntime", reason="instale requirements-pln.txt")
pytest.importorskip("tokenizers", reason="instale requirements-pln.txt")


@pytest.fixture(scope="module")
def classificador() -> ClassificadorDeIntencoes:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        instancia = get_classifier()
        instancia.classify("aquecimento dos artefatos")
        return instancia


@pytest.fixture(scope="module")
def conjunto_de_teste() -> list[dict]:
    with DATASET.open(encoding="utf-8") as arquivo:
        return [linha for linha in csv.DictReader(arquivo) if linha["split"] == "teste"]


class TestClassificacaoDeSolicitacoes:
    def test_consulta_de_status_aciona_o_handler_especifico(
        self, classificador
    ) -> None:
        resultado = classificador.classify(
            "qual é o status da extensão da Linha 5-Lilás?"
        )

        assert resultado.macrointencao == "CONSULTA"
        assert resultado.intencao == "consulta_status_projeto"
        assert resultado.handler == "handler:consulta_status_projeto"
        assert resultado.resposta_sugerida is None

    def test_solicitacao_fora_do_catalogo_e_marcada_como_fora_de_escopo(
        self, classificador
    ) -> None:
        resultado = classificador.classify("qual a previsão do tempo para amanhã?")

        assert resultado.macrointencao == "FORA_DE_ESCOPO"
        assert resultado.intencao is None

    def test_intencao_de_baixa_confianca_cai_no_fluxo_generico(
        self, classificador
    ) -> None:
        """Roteia pela macro, mas não aciona um handler específico incerto."""

        resultado = classificador.classify("há bloqueios registrados no Linha 15-Prata?")

        assert resultado.roteada
        assert not resultado.handler_especifico
        assert resultado.handler.startswith("fluxo genérico")

    def test_alternativas_vem_ordenadas_por_confianca(self, classificador) -> None:
        resultado = classificador.classify("qual o orçamento do Linha 4-Amarela?")

        confiancas = [confianca for _, confianca in resultado.alternativas]
        assert confiancas == sorted(confiancas, reverse=True)
        assert len(resultado.alternativas) == 3

    def test_top_k_controla_a_quantidade_de_alternativas(self, classificador) -> None:
        resultado = classificador.classify("qual o orçamento do projeto?", top_k=5)

        assert len(resultado.alternativas) == 5

    def test_atalho_de_modulo_usa_a_instancia_compartilhada(self) -> None:
        assert isinstance(classify("qual o prazo do Linha 2-Verde?"), Classificacao)


class TestLimiaresDeConfianca:
    def test_limiares_sao_os_calibrados_na_validacao(self, classificador) -> None:
        assert classificador.artefato.limiar_macro == pytest.approx(0.550)
        assert classificador.artefato.limiar_intencao == pytest.approx(0.700)

    def test_macro_abaixo_do_limiar_recebe_resposta_de_limitacao(
        self, classificador, conjunto_de_teste
    ) -> None:
        """O RNF11 exige mensagem controlada, não um handler adivinhado."""

        indefinidas = [
            resultado
            for resultado in map(
                classificador.classify, [l["texto"] for l in conjunto_de_teste]
            )
            if resultado.macrointencao == UNDEFINED_MACRO
        ]

        assert indefinidas, "nenhuma solicitação do teste ficou abaixo do limiar"
        for resultado in indefinidas:
            assert resultado.intencao is None
            assert resultado.resposta_sugerida == LIMITATION_ANSWER
            assert not resultado.roteada

    def test_macro_e_intencao_nunca_saem_incoerentes(
        self, classificador, conjunto_de_teste
    ) -> None:
        """Anunciar uma macrointenção e um handler de outra quebraria o roteamento."""

        intencao2macro = classificador.artefato.intencao2macro
        for linha in conjunto_de_teste:
            resultado = classificador.classify(linha["texto"])
            if resultado.intencao is not None:
                assert intencao2macro[resultado.intencao] == resultado.macrointencao


@pytest.fixture(scope="module")
def predicoes(classificador, conjunto_de_teste):
    """Previsões sobre o conjunto de teste, reaproveitadas pelas métricas."""

    from sklearn.metrics import accuracy_score, f1_score

    textos = [linha["texto"] for linha in conjunto_de_teste]
    atributos = classificador.vectorize(textos)
    modelo = classificador.artefato.modelo

    probabilidades = modelo.predict_proba_intencao(atributos)
    previstas = modelo.classes_[probabilidades.argmax(axis=1)]
    esperadas = np.array([linha["intencao"] for linha in conjunto_de_teste])
    _, probabilidades_macro = modelo.predict_proba_macro(atributos)

    return {
        "acuracia": accuracy_score(esperadas, previstas),
        "f1": f1_score(esperadas, previstas, average="macro", zero_division=0),
        "confianca_macro": probabilidades_macro.max(axis=1),
        "confianca_intencao": probabilidades.max(axis=1),
        "acerto": previstas == esperadas,
        "atributos": atributos,
    }


class TestFidelidadeAoBenchmark:
    """A inferência tem de reproduzir os números registrados na documentação."""

    def test_dimensao_dos_atributos_e_a_esperada_pelo_modelo(
        self, classificador, predicoes
    ) -> None:
        esperada = classificador.artefato.modelo.macro_clf.n_features_in_

        assert predicoes["atributos"].shape[1] == esperada

    def test_acuracia_da_intencao_no_teste(self, predicoes) -> None:
        assert predicoes["acuracia"] == pytest.approx(0.7383, abs=0.0002)

    def test_f1_macro_da_intencao_no_teste(self, predicoes) -> None:
        assert predicoes["f1"] == pytest.approx(0.7401, abs=0.0002)

    def test_efeito_dos_limiares_reproduz_a_documentacao(
        self, classificador, predicoes
    ) -> None:
        limiar_macro = classificador.artefato.limiar_macro
        limiar_intencao = classificador.artefato.limiar_intencao

        abaixo = predicoes["confianca_macro"] < limiar_macro
        generico = ~abaixo & (predicoes["confianca_intencao"] < limiar_intencao)
        aceitos = ~abaixo & ~generico

        assert abaixo.sum() == 14
        assert generico.sum() == 305
        assert predicoes["acerto"][aceitos].mean() == pytest.approx(0.8775, abs=0.0002)


class TestCarregamentoDosArtefatos:
    def test_word2vec_traz_o_vocabulario_do_corpus(self, classificador) -> None:
        assert len(classificador.word2vec.wv) == 577
        assert classificador.word2vec.wv.vector_size == 200

    def test_token_fora_do_vocabulario_nao_quebra_a_vetorizacao(
        self, classificador
    ) -> None:
        vetor = classificador._vetor_w2v(["zzzzz", "wwwww"])

        assert vetor.shape == (200,)
        assert not vetor.any()

    def test_o_encoder_roda_sem_pytorch(self, classificador) -> None:
        """A inferencia nao deve arrastar torch nem transformers."""

        import sys

        classificador.classify("qual o prazo do Linha 2-Verde?")

        assert "torch" not in sys.modules
        assert "transformers" not in sys.modules

    def test_warmup_carrega_os_artefatos_antecipadamente(self, classificador) -> None:
        """A API deve pagar a carga na subida, nao na primeira requisicao."""

        classificador.warmup()

        assert classificador._encoder is not None
        assert classificador._word2vec is not None

    def test_bloco_desconhecido_e_recusado(self, classificador) -> None:
        artefato = classificador.artefato
        original = artefato.blocos_da_representacao
        object.__setattr__(artefato, "blocos_da_representacao", ["inexistente"])
        try:
            with pytest.raises(ValueError, match="Bloco de representação"):
                classificador.vectorize(["texto"])
        finally:
            object.__setattr__(artefato, "blocos_da_representacao", original)
