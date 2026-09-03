"""Classificador hierárquico de intenções do núcleo de PLN.

Este módulo é o **lar canônico** das definições que o artefato treinado
referencia. Elas nasceram no topo do notebook
`src/notebooks/classificador_intencoes_metro.ipynb`, e o `joblib` gravou
referências a `__main__.identidade` e `__main__.ClassificadorHierarquico`. Um
artefato assim só carrega de dentro do notebook: de qualquer código importável,
`joblib.load` falha com `AttributeError`.

Trazer as duas definições para cá resolve a origem do problema. O script
`src/notebooks/migrar_artefato_classificador.py` reescreve o artefato apontando
para este módulo, e a partir daí ele carrega de qualquer processo.

A arquitetura é hierárquica, conforme a Seção 8.10.2 do `Projeto.md`: a primeira
etapa prevê a macrointenção e a segunda aciona um especialista treinado apenas
com as intenções daquele grupo. O ganho medido sobre a arquitetura plana foi de
0,0857 de F1-macro na intenção específica — maior que qualquer diferença entre
representações.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

ARTIFACT_DIR = Path(__file__).resolve().parents[3] / "notebooks" / "artefatos"
ARTIFACT_PATH = ARTIFACT_DIR / "classificador_intencoes.joblib"
WORD2VEC_PATH = ARTIFACT_DIR / "word2vec_portfolio.model"

MACRO_INTENTS = ("CONSULTA", "TRANSACAO", "ALERTA", "FORA_DE_ESCOPO")

# Chaves que o artefato precisa expor para ser utilizável na inferência.
REQUIRED_ARTIFACT_KEYS = frozenset(
    {
        "tfidf_palavras",
        "tfidf_caracteres",
        "svd_palavras",
        "svd_caracteres",
        "scalers",
        "modelo",
        "config_preprocessamento",
        "representacao",
        "blocos_da_representacao",
        "limiar_macro",
        "limiar_intencao",
        "intencao2macro",
    }
)


def identidade(tokens: Sequence[str]) -> Sequence[str]:
    """Analyzer do TF-IDF para texto já tokenizado.

    Precisa ser uma função nomeada em módulo importável — uma `lambda` não é
    serializável, e uma função definida no notebook prende o artefato a ele.
    """

    return tokens


class ClassificadorHierarquico:
    """Etapa 1: macrointenção. Etapa 2: especialista da macro predita."""

    def __init__(self, fabrica=None) -> None:
        self.fabrica = fabrica
        self.macro_clf = None
        self.especialistas: dict[str, Any] = {}
        # Macrointenção com uma única intenção não precisa de especialista.
        self.unica: dict[str, Any] = {}

    def fit(self, X, y_macro, y_int) -> "ClassificadorHierarquico":
        self.macro_clf = self.fabrica()
        self.macro_clf.fit(X, y_macro)
        for macro in np.unique(y_macro):
            mask = y_macro == macro
            classes = np.unique(y_int[mask])
            if len(classes) == 1:
                self.unica[macro] = classes[0]
            else:
                self.especialistas[macro] = self.fabrica().fit(X[mask], y_int[mask])
        return self

    def predict(self, X):
        macros = self.macro_clf.predict(X)
        preds = np.empty(len(macros), dtype=object)
        for macro in np.unique(macros):
            mask = macros == macro
            if macro in self.unica:
                preds[mask] = self.unica[macro]
            else:
                preds[mask] = self.especialistas[macro].predict(X[mask])
        return preds

    def predict_proba_intencao(self, X):
        """P(macro) * P(intenção | macro), na ordem de ``self.classes_``."""

        p_macro = self.macro_clf.predict_proba(X)
        colunas, nomes = [], []
        for j, macro in enumerate(self.macro_clf.classes_):
            if macro in self.unica:
                colunas.append(p_macro[:, j : j + 1])
                nomes.append(self.unica[macro])
            else:
                especialista = self.especialistas[macro]
                colunas.append(especialista.predict_proba(X) * p_macro[:, j : j + 1])
                nomes.extend(list(especialista.classes_))
        probabilidades = np.hstack(colunas)
        self.classes_ = np.array(nomes)
        return probabilidades

    def predict_proba_macro(self, X):
        return self.macro_clf.classes_, self.macro_clf.predict_proba(X)


@dataclass(frozen=True)
class ArtefatoClassificador:
    """Conteúdo do artefato treinado, com os limiares calibrados na validação."""

    modelo: ClassificadorHierarquico
    tfidf_palavras: Any
    tfidf_caracteres: Any
    svd_palavras: Any
    svd_caracteres: Any
    scalers: dict[str, Any]
    config_preprocessamento: dict[str, Any]
    representacao: str
    blocos_da_representacao: list[str]
    limiar_macro: float
    limiar_intencao: float
    intencao2macro: dict[str, str]

    @property
    def intencoes(self) -> list[str]:
        return sorted(self.intencao2macro)

    @property
    def macrointencoes(self) -> list[str]:
        return sorted(set(self.intencao2macro.values()))


def load_artifact(path: Path | None = None) -> ArtefatoClassificador:
    """Carrega o artefato treinado e valida que ele está completo.

    Levanta ``FileNotFoundError`` quando o arquivo não existe e ``ValueError``
    quando faltam chaves — falhar aqui é preferível a descobrir a ausência no
    meio de uma inferência.
    """

    import joblib

    caminho = path or ARTIFACT_PATH
    if not caminho.exists():
        raise FileNotFoundError(
            f"Artefato do classificador não encontrado em {caminho}. "
            "Execute src/notebooks/migrar_artefato_classificador.py."
        )

    dados = joblib.load(caminho)
    ausentes = REQUIRED_ARTIFACT_KEYS - set(dados)
    if ausentes:
        raise ValueError(
            "Artefato do classificador incompleto; faltam as chaves: "
            + ", ".join(sorted(ausentes))
        )

    return ArtefatoClassificador(
        **{chave: dados[chave] for chave in REQUIRED_ARTIFACT_KEYS}
    )
