"""Inferência do classificador de intenções (Seção 8.10.3 do Projeto.md).

Os testes carregam os artefatos reais — inclusive o encoder BERT, baixado na
primeira execução. São marcados como lentos e compartilham uma única instância.
"""

import csv
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

from app.nlp.inference import (
    BERT_MODEL_ENV,
    BERT_REVISION_ENV,
    DEFAULT_BERT_MODEL,
    DEFAULT_BERT_REVISION,
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
REPORT_PATH = DATASET.with_name("avaliacao_classificador_intencoes.json")
RNF06_F1_MACRO_TARGET = 0.80

# A representacao vencedora usa o BERTimbau, carregado fora do joblib.
# Sem as dependencias de requirements-pln.txt nao ha o que exercitar.
pytest.importorskip("torch", reason="instale requirements-pln.txt")
pytest.importorskip("transformers", reason="instale requirements-pln.txt")


#: Marcado pela #228 (S4-32B): este arquivo cruza fronteira entre
#: componentes (API, modelo, banco ou servico externo). Rodar so estes com
#: `pytest -m integration`.
pytestmark = pytest.mark.integration


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


def _round4(valor: float) -> float:
    return round(float(valor), 4)


def _write_json_if_changed(path: Path, payload: dict) -> None:
    conteudo = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != conteudo:
        path.write_text(conteudo, encoding="utf-8")


def _build_evaluation_report(classificador, conjunto_de_teste, predicoes) -> dict:
    from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

    esperadas = predicoes["esperadas"]
    previstas = predicoes["previstas"]
    classes = classificador.artefato.intencoes
    precisao, recall, f1, suporte = precision_recall_fscore_support(
        esperadas,
        previstas,
        labels=classes,
        zero_division=0,
    )

    metricas_por_classe = {
        classe: {
            "precisao": _round4(precisao[indice]),
            "recall": _round4(recall[indice]),
            "f1": _round4(f1[indice]),
            "suporte": int(suporte[indice]),
        }
        for indice, classe in enumerate(classes)
    }
    piores_classes = sorted(
        (
            {"classe": classe, **metricas}
            for classe, metricas in metricas_por_classe.items()
        ),
        key=lambda item: (item["f1"], item["recall"], item["precisao"], item["classe"]),
    )[:5]

    f1_macro = _round4(predicoes["f1"])
    meta_atingida = f1_macro >= RNF06_F1_MACRO_TARGET
    return {
        "RNF06": {
            "meta_f1_macro_intencao_especifica": RNF06_F1_MACRO_TARGET,
            "f1_macro_intencao_especifica": f1_macro,
            "aderente": meta_atingida,
            "status": "aderente" if meta_atingida else "nao_aderente",
            "conclusao": (
                "RNF06 atendido para a intencao especifica."
                if meta_atingida
                else "RNF06 nao atendido: F1 macro da intencao especifica abaixo de 0,80."
            ),
        },
        "protocolo": {
            "dataset": "src/notebooks/artefatos/dataset_intencoes.csv",
            "filtro": "split == teste",
            "tamanho_teste": len(conjunto_de_teste),
            "classificador": "src/backend/app/nlp/",
            "sem_retreino": True,
        },
        "metricas_globais": {
            "acuracia_intencao_especifica": _round4(predicoes["acuracia"]),
            "f1_macro_intencao_especifica": f1_macro,
        },
        "metricas_por_classe": metricas_por_classe,
        "matriz_confusao": {
            "labels": classes,
            "valores": confusion_matrix(
                esperadas,
                previstas,
                labels=classes,
            ).astype(int).tolist(),
        },
        "piores_classes": piores_classes,
        "limitacoes": [
            "Conjunto sintetico, ainda sem validacao com solicitacoes reais do dominio.",
            "Medicao considera somente a intencao especifica prevista pelo modelo, antes dos limiares de roteamento.",
            "Classes com baixo suporte e fronteiras entre consulta e transacao concentram parte dos erros.",
        ],
    }


class TestClassificacaoDeSolicitacoes:
    @pytest.mark.parametrize("text,macro,specific", [
        ("fale sobre os Objetos perdidos", "CONSULTA", None),
        ("fale sobre o Bilhete digital", "CONSULTA", None),
        ("Bilhete digital", "CONSULTA", None),
        ("Como funciona o bilhete digital?", "CONSULTA", None),
        ("Mostre o status do projeto PRJ-0442", "CONSULTA", "consulta_status_projeto"),
        ("Mostre o status do projeto XPTO", "CONSULTA", "consulta_status_projeto"),
        ("Qual é o status do projeto PRJ-0442?", "CONSULTA", "consulta_status_projeto"),
        ("Reserve uma sala de reunião para amanhã", "FORA_DE_ESCOPO", None),
        ("Agende uma reunião amanhã", "FORA_DE_ESCOPO", None),
    ])
    def test_casos_congelados_issue_282(self, classificador, text, macro, specific):
        result = classificador.classify(text)
        assert result.macrointencao == macro
        assert result.intencao == specific
        assert result.regra_roteamento is not None
        if macro == "FORA_DE_ESCOPO":
            assert result.handler == "limitacao:agendamento"
            assert result.resposta_sugerida
        else:
            assert result.resposta_sugerida is None

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

        resultado = classificador.classify("preciso de informações do projeto")

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
        assert classificador.artefato.limiar_macro == pytest.approx(0.525)
        assert classificador.artefato.limiar_intencao == pytest.approx(0.350)

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
        "esperadas": esperadas,
        "previstas": previstas,
        "confianca_macro": probabilidades_macro.max(axis=1),
        "confianca_intencao": probabilidades.max(axis=1),
        "acerto": previstas == esperadas,
        "atributos": atributos,
    }


@pytest.fixture(scope="module")
def relatorio_avaliacao(classificador, conjunto_de_teste, predicoes):
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


class TestFidelidadeAoBenchmark:
    """A inferência tem de reproduzir os números registrados na documentação."""

    def test_dimensao_dos_atributos_e_a_esperada_pelo_modelo(
        self, classificador, predicoes
    ) -> None:
        esperada = classificador.artefato.modelo.macro_clf.n_features_in_

        assert predicoes["atributos"].shape[1] == esperada

    def test_medicao_usa_somente_split_de_teste(self, conjunto_de_teste) -> None:
        assert conjunto_de_teste
        assert {linha["split"] for linha in conjunto_de_teste} == {"teste"}

    def test_acuracia_da_intencao_no_teste(self, predicoes) -> None:
        assert predicoes["acuracia"] == pytest.approx(0.839648, abs=0.000002)

    def test_f1_macro_da_intencao_no_teste(self, predicoes) -> None:
        assert predicoes["f1"] == pytest.approx(0.832724, abs=0.000002)

    def test_relatorio_registra_meta_atingida(self, relatorio_avaliacao) -> None:
        assert relatorio_avaliacao["versao"] == 2
        assert relatorio_avaliacao["teste_usado_na_selecao"] is False
        assert relatorio_avaliacao["teste"]["intencao"] == {
            "acuracia": pytest.approx(0.839648),
            "f1_macro": pytest.approx(0.832724),
        }
        assert relatorio_avaliacao["tamanhos"]["teste"] == 1135
        assert relatorio_avaliacao["tamanhos"]["sinteticos_adicionais"] == 1450
        assert len(relatorio_avaliacao["matriz_confusao"]["labels"]) == 31
        assert len(relatorio_avaliacao["metricas_por_classe"]) == 31
        assert REPORT_PATH.exists()

    def test_efeito_dos_limiares_reproduz_a_documentacao(
        self, classificador, predicoes
    ) -> None:
        limiar_macro = classificador.artefato.limiar_macro
        limiar_intencao = classificador.artefato.limiar_intencao

        abaixo = predicoes["confianca_macro"] < limiar_macro
        generico = ~abaixo & (predicoes["confianca_intencao"] < limiar_intencao)
        aceitos = ~abaixo & ~generico

        assert abaixo.sum() == 10
        assert generico.sum() == 63
        assert predicoes["acerto"][aceitos].mean() >= 0.85


class TestCarregamentoDosArtefatos:
    def test_tfidf_preserva_acento_e_negacao_no_vocabulario(self, classificador) -> None:
        vocabulario = classificador.artefato.tfidf_palavras.vocabulary_

        assert "não" in vocabulario
        assert "previsão" in vocabulario

    @pytest.mark.parametrize(
        "model,revision",
        [
            (DEFAULT_BERT_MODEL, DEFAULT_BERT_REVISION),
            ("organizacao/modelo-controlado", "a" * 40),
        ],
    )
    def test_encoder_baixa_modelo_e_tokenizador_da_mesma_revisao(
        self,
        monkeypatch,
        model,
        revision,
    ) -> None:
        carregamentos = []

        class FakeTokenizer:
            pass

        class FakeModel:
            def eval(self):
                carregamentos.append(("eval",))
                return self

        def fake_tokenizer(repo_id, *, revision):
            carregamentos.append(("tokenizer", repo_id, revision))
            return FakeTokenizer()

        def fake_model(repo_id, *, revision):
            carregamentos.append(("model", repo_id, revision))
            return FakeModel()

        monkeypatch.setattr(
            "transformers.AutoTokenizer.from_pretrained", fake_tokenizer
        )
        monkeypatch.setattr("transformers.AutoModel.from_pretrained", fake_model)
        if model == DEFAULT_BERT_MODEL:
            monkeypatch.delenv(BERT_MODEL_ENV, raising=False)
            monkeypatch.delenv(BERT_REVISION_ENV, raising=False)
        else:
            monkeypatch.setenv(BERT_MODEL_ENV, model)
            monkeypatch.setenv(BERT_REVISION_ENV, revision)

        classificador = ClassificadorDeIntencoes()
        modelo, tokenizador = classificador._bert

        assert isinstance(modelo, FakeModel)
        assert isinstance(tokenizador, FakeTokenizer)
        assert carregamentos == [
            ("tokenizer", model, revision),
            ("model", model, revision),
            ("eval",),
        ]

    @pytest.mark.parametrize("revision", ["main", "v1.0", "", "a" * 39])
    def test_encoder_recusa_revisao_mutavel_ou_invalida(
        self, monkeypatch, revision
    ) -> None:
        monkeypatch.setenv(BERT_REVISION_ENV, revision)

        with pytest.raises(ValueError, match="SHA hexadecimal de 40 caracteres"):
            ClassificadorDeIntencoes()._bert

    def test_o_encoder_usa_bertimbau(self, classificador) -> None:
        """O bloco semantico selecionado e o BERTimbau cased."""

        classificador.classify("qual o prazo do Linha 2-Verde?")

        assert "torch" in sys.modules
        assert "transformers" in sys.modules
        assert classificador._bert[0].config.name_or_path == (
            "neuralmind/bert-base-portuguese-cased"
        )

    def test_warmup_carrega_os_artefatos_antecipadamente(self, classificador) -> None:
        """A API deve pagar a carga na subida, nao na primeira requisicao."""

        classificador.warmup()

        assert classificador._encoder is not None

    def test_bloco_desconhecido_e_recusado(self, classificador) -> None:
        artefato = classificador.artefato
        original = artefato.blocos_da_representacao
        object.__setattr__(artefato, "blocos_da_representacao", ["inexistente"])
        try:
            with pytest.raises(ValueError, match="Bloco de representação"):
                classificador.vectorize(["texto"])
        finally:
            object.__setattr__(artefato, "blocos_da_representacao", original)
