"""Artefato do classificador hierárquico de intenções (Seção 8.10 do Projeto.md)."""

import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

from app.nlp.classifier import (
    ARTIFACT_PATH,
    MACRO_INTENTS,
    ClassificadorHierarquico,
    identidade,
    load_artifact,
)
from app.nlp.preprocessing import SELECTED_CONFIG

BACKEND_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def artefato():
    """Carregado uma vez: são 13 MB de vetorizadores e modelo."""

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return load_artifact()


class TestArtefatoCarregavel:
    """A migração existe para o artefato deixar de depender do notebook."""

    def test_carrega_em_um_processo_limpo(self) -> None:
        """Carregar dentro da suíte não provaria nada: o módulo já está importado."""

        codigo = (
            f"import sys, warnings; sys.path.insert(0, {str(BACKEND_DIR)!r})\n"
            "warnings.filterwarnings('ignore')\n"
            "from app.nlp.classifier import load_artifact\n"
            "print(load_artifact().representacao)\n"
        )
        resultado = subprocess.run(
            [sys.executable, "-c", codigo], capture_output=True, text=True
        )

        assert resultado.returncode == 0, resultado.stderr
        assert "Híbrido completo" in resultado.stdout

    def test_o_modelo_referencia_o_modulo_e_nao_o_notebook(self, artefato) -> None:
        assert type(artefato.modelo).__module__ == "app.nlp.classifier"
        assert artefato.tfidf_palavras.analyzer.__module__ == "app.nlp.classifier"

    def test_ausencia_do_arquivo_e_reportada_com_a_saida(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="migrar_artefato_classificador"):
            load_artifact(tmp_path / "inexistente.joblib")

    def test_artefato_incompleto_falha_ao_carregar(self, tmp_path: Path) -> None:
        import joblib

        caminho = tmp_path / "parcial.joblib"
        joblib.dump({"modelo": None, "limiar_macro": 0.55}, caminho)

        with pytest.raises(ValueError, match="incompleto"):
            load_artifact(caminho)


class TestConteudoDoArtefato:
    def test_preprocessamento_gravado_e_o_mesmo_do_modulo(self, artefato) -> None:
        """Se divergirem, a inferência tokeniza diferente do treino."""

        assert artefato.config_preprocessamento == dict(SELECTED_CONFIG)

    def test_limiares_sao_os_calibrados_na_validacao(self, artefato) -> None:
        assert artefato.limiar_macro == pytest.approx(0.550)
        assert artefato.limiar_intencao == pytest.approx(0.700)

    def test_catalogo_tem_as_trinta_e_uma_intencoes(self, artefato) -> None:
        assert len(artefato.intencoes) == 31
        assert set(artefato.macrointencoes) == set(MACRO_INTENTS)

    def test_toda_intencao_pertence_a_uma_macrointencao_conhecida(
        self, artefato
    ) -> None:
        assert set(artefato.intencao2macro.values()) <= set(MACRO_INTENTS)

    def test_representacao_declara_os_quatro_blocos_hibridos(self, artefato) -> None:
        assert artefato.blocos_da_representacao == [
            "svd_palavra",
            "svd_char",
            "w2v",
            "bert",
        ]
        assert set(artefato.scalers) == set(artefato.blocos_da_representacao)


class TestModeloHierarquico:
    def test_um_especialista_por_macrointencao(self, artefato) -> None:
        cobertas = set(artefato.modelo.especialistas) | set(artefato.modelo.unica)

        assert cobertas == set(MACRO_INTENTS)

    def test_os_especialistas_somam_as_trinta_e_uma_intencoes(self, artefato) -> None:
        total = sum(
            len(especialista.classes_)
            for especialista in artefato.modelo.especialistas.values()
        )

        assert total + len(artefato.modelo.unica) == 31

    def test_probabilidades_de_intencao_somam_um(self, artefato) -> None:
        X = self._entrada_sintetica(artefato)

        probabilidades = artefato.modelo.predict_proba_intencao(X)

        assert probabilidades.shape == (3, 31)
        assert probabilidades.sum(axis=1) == pytest.approx(1.0)

    def test_probabilidades_de_macro_somam_um(self, artefato) -> None:
        macros, probabilidades = artefato.modelo.predict_proba_macro(
            self._entrada_sintetica(artefato)
        )

        assert set(macros) == set(MACRO_INTENTS)
        assert probabilidades.sum(axis=1) == pytest.approx(1.0)

    def test_predict_devolve_intencoes_do_catalogo(self, artefato) -> None:
        previstas = artefato.modelo.predict(self._entrada_sintetica(artefato))

        assert set(previstas) <= set(artefato.intencoes)

    @staticmethod
    def _entrada_sintetica(artefato) -> np.ndarray:
        """Matriz na dimensão que o modelo espera.

        Exercita a mecânica do classificador sem depender do Word2Vec e do
        BERT, que compõem os atributos reais.
        """

        dimensao = artefato.modelo.macro_clf.n_features_in_
        return np.random.default_rng(0).normal(size=(3, dimensao))


class TestClassificadorHierarquicoIsolado:
    """A lógica da classe, independente do artefato treinado."""

    @staticmethod
    def _treinar() -> ClassificadorHierarquico:
        from sklearn.linear_model import LogisticRegression

        X = np.array([[0.0], [0.1], [1.0], [1.1], [2.0], [2.1]])
        y_macro = np.array(["A", "A", "B", "B", "C", "C"])
        y_int = np.array(["a1", "a2", "b1", "b2", "c1", "c1"])
        fabrica = lambda: LogisticRegression(max_iter=1000)  # noqa: E731

        return ClassificadorHierarquico(fabrica).fit(X, y_macro, y_int)

    def test_macro_com_uma_unica_intencao_dispensa_especialista(self) -> None:
        modelo = self._treinar()

        assert modelo.unica == {"C": "c1"}
        assert set(modelo.especialistas) == {"A", "B"}

    def test_predicao_usa_o_especialista_da_macro_prevista(self) -> None:
        modelo = self._treinar()

        assert set(modelo.predict(np.array([[0.05], [2.05]]))) <= {"a1", "a2", "c1"}

    def test_probabilidade_conjunta_cobre_todas_as_intencoes(self) -> None:
        modelo = self._treinar()

        probabilidades = modelo.predict_proba_intencao(np.array([[0.05]]))

        assert set(modelo.classes_) == {"a1", "a2", "b1", "b2", "c1"}
        assert probabilidades.sum() == pytest.approx(1.0)


class TestAnalyzer:
    def test_identidade_devolve_os_tokens_recebidos(self) -> None:
        tokens = ["qual", "praz", "projet"]

        assert identidade(tokens) is tokens

    def test_o_artefato_versionado_esta_no_lugar_esperado(self) -> None:
        assert ARTIFACT_PATH.exists()
