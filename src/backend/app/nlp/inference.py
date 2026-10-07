"""Inferência do classificador de intenções.

Recebe uma solicitação em texto e devolve a macrointenção, a intenção
específica e as confianças, aplicando os dois limiares calibrados na validação
e registrados na Seção 8.10.7 do `Projeto.md`.

As transformações reproduzem **exatamente** as ajustadas no treino, na ordem em
que foram compostas. Qualquer divergência — outra tokenização, outra ordem de
blocos, normalização ausente — produz atributos que o modelo nunca viu, e o
resultado seria silenciosamente errado em vez de falhar.

A representação vencedora concatena TF-IDF de palavras, TF-IDF de caracteres
e embeddings congelados do BERTimbau. O encoder
`neuralmind/bert-base-portuguese-cased` recebe o texto cru, preservando caixa e
acentos, e é baixado do Hugging Face na primeira execução. A combinação foi
selecionada apenas na validação; o teste fixo foi aberto uma vez depois disso.

Os limiares não são detalhe de implementação. A intenção específica atingiu
0,8327 de F1-macro no teste; abaixo do limiar, a solicitação
segue para o fluxo genérico da macrointenção ou recebe resposta controlada de
limitação, em vez de acionar um handler errado. É o comportamento conservador
que o RNF04 e o RNF11 exigem.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from app.nlp.classifier import (
    ARTIFACT_DIR,
    ArtefatoClassificador,
    load_artifact,
)

CATALOG_PATH = ARTIFACT_DIR / "catalogo_intencoes.json"

DEFAULT_BERT_MODEL = "neuralmind/bert-base-portuguese-cased"
BERT_MODEL_ENV = "PLN_BERT_MODEL"
DEFAULT_BERT_REVISION = "94d69c95f98f7d5b2a8700c420230ae10def0baa"
BERT_REVISION_ENV = "PLN_BERT_REVISION"
MAX_SEQUENCE_LENGTH = 64

_IMMUTABLE_REVISION_RE = re.compile(r"^[0-9a-f]{40}$")

UNDEFINED_MACRO = "INDEFINIDA"

_BATCH_SIZE = 64

LIMITATION_ANSWER = (
    "Não consegui identificar com segurança o que você precisa dentro do "
    "portfólio ou nos temas da base. Pode reformular indicando o tema e a "
    "informação desejada? Por exemplo: 'Como funciona o Bilhete digital?' "
    "ou 'Qual é o status do projeto PRJ-0442?'"
)
LIMITATION_FLOW = "Resposta padrão de limitação (RF08)"


def _bert_revision() -> str:
    """Resolve somente snapshots imutáveis do Hugging Face."""

    revisao = os.getenv(BERT_REVISION_ENV, DEFAULT_BERT_REVISION).strip()
    if not _IMMUTABLE_REVISION_RE.fullmatch(revisao):
        raise ValueError(
            f"{BERT_REVISION_ENV} deve ser o SHA hexadecimal de 40 caracteres "
            "de um commit imutável do Hugging Face."
        )
    return revisao


@dataclass(frozen=True)
class Classificacao:
    """Resultado da classificação de uma solicitação."""

    texto: str
    macrointencao: str
    confianca_macro: float
    intencao: str | None
    confianca_intencao: float
    fluxo: str
    handler: str
    alternativas: list[tuple[str, float]] = field(default_factory=list)
    resposta_sugerida: str | None = None
    regra_roteamento: str | None = None

    @property
    def roteada(self) -> bool:
        """A solicitação foi aceita pelo modelo ou por regra explícita de domínio."""

        return self.macrointencao != UNDEFINED_MACRO

    @property
    def handler_especifico(self) -> bool:
        """A intenção passou do limiar e um handler dedicado pode ser acionado."""

        return self.intencao is not None


class ClassificadorDeIntencoes:
    """Carrega os artefatos uma vez e classifica solicitações.

    O carregamento é adiado até a primeira classificação: o encoder BERT ocupa
    centenas de megabytes e não deve ser pago por quem apenas importa o módulo.
    """

    def __init__(self, artefato: ArtefatoClassificador | None = None) -> None:
        self._artefato = artefato
        self._encoder = None

    @property
    def artefato(self) -> ArtefatoClassificador:
        if self._artefato is None:
            self._artefato = load_artifact()
        return self._artefato

    def classify(self, texto: str, top_k: int = 3) -> Classificacao:
        """Classifica uma solicitação e decide o roteamento pelos limiares."""

        atributos = self.vectorize([texto])
        modelo = self.artefato.modelo

        probabilidades = modelo.predict_proba_intencao(atributos)[0]
        classes = modelo.classes_
        macros, probabilidades_macro = modelo.predict_proba_macro(atributos)
        probabilidades_macro = probabilidades_macro[0]

        ordem = np.argsort(probabilidades)[::-1][:top_k]
        macro = str(macros[int(np.argmax(probabilidades_macro))])
        confianca_macro = float(probabilidades_macro.max())
        intencao = str(classes[ordem[0]])
        confianca_intencao = float(probabilidades[ordem[0]])

        roteia = confianca_macro >= self.artefato.limiar_macro
        especifico = (
            roteia
            and confianca_intencao >= self.artefato.limiar_intencao
            and macro != "FORA_DE_ESCOPO"
            # A intenção prevista vem do argmax sobre as 31 classes, e a
            # macrointenção do argmax sobre as 4. Como a probabilidade da
            # intenção é conjunta — P(macro) x P(intenção | macro) —, um limiar
            # acima de 0,5 já força as duas a coincidirem. A condição abaixo
            # não depende disso: se alguém recalibrar o limiar para baixo, a
            # saída continua coerente em vez de anunciar uma macrointenção e um
            # handler de outra.
            and self.artefato.intencao2macro.get(intencao) == macro
        )

        resultado = Classificacao(
            texto=texto,
            macrointencao=macro if roteia else UNDEFINED_MACRO,
            confianca_macro=round(confianca_macro, 4),
            intencao=intencao if especifico else None,
            confianca_intencao=round(confianca_intencao, 4),
            fluxo=_fluxo_da_macro(macro) if roteia else LIMITATION_FLOW,
            handler=(
                f"handler:{intencao}"
                if especifico
                else (f"fluxo genérico de {macro}" if roteia else "limitacao")
            ),
            alternativas=[
                (str(classes[i]), round(float(probabilidades[i]), 4)) for i in ordem
            ],
            resposta_sugerida=None if roteia else LIMITATION_ANSWER,
        )
        from app.nlp.routing import apply_domain_routes

        resultado = apply_domain_routes(resultado)
        if resultado.regra_roteamento:
            # Regra determinística não vira probabilidade 1.0. Informar a
            # probabilidade real da classe selecionada, mesmo abaixo do limiar.
            indice_macro = list(macros).index(resultado.macrointencao)
            confianca_especifica = (
                float(probabilidades[list(classes).index(resultado.intencao)])
                if resultado.intencao else 0.0
            )
            resultado = replace(
                resultado,
                confianca_macro=round(float(probabilidades_macro[indice_macro]), 4),
                confianca_intencao=round(confianca_especifica, 4),
            )
        return resultado

    def vectorize(self, textos: Sequence[str]) -> Any:
        """Aplica as mesmas transformações ajustadas no treino, na mesma ordem."""

        from scipy import sparse
        textos = list(textos)
        artefato = self.artefato

        partes = []
        for bloco in artefato.blocos_da_representacao:
            if bloco == "tfidf_palavra":
                partes.append(artefato.tfidf_palavras.transform(textos))
                continue
            if bloco == "tfidf_char":
                partes.append(artefato.tfidf_caracteres.transform(textos))
                continue
            if bloco == "bertimbau":
                peso = float(artefato.scalers.get(bloco, 1.0))
                partes.append(sparse.csr_matrix(self._encode(textos) * peso))
                continue
            raise ValueError(f"Bloco de representação desconhecido: {bloco}")

        if any(sparse.issparse(parte) for parte in partes):
            return sparse.hstack(
                [sparse.csr_matrix(parte) for parte in partes], format="csr"
            )
        return np.hstack(partes) if len(partes) > 1 else partes[0]

    def warmup(self) -> None:
        """Carrega todos os artefatos antecipadamente.

        A carga preguiçosa serve aos testes, mas em produção faria a primeira
        pessoa a usar o agente pagar o carregamento inteiro dentro da própria
        requisição. A API deve chamar isto na subida.
        """

        self.classify("aquecimento do pipeline de PLN")

    def _encode(self, textos: Sequence[str]) -> np.ndarray:
        """Embeddings BERTimbau congelados, com média sobre tokens válidos."""

        import torch
        from sklearn.preprocessing import normalize

        modelo, tokenizador = self._bert
        lotes = []
        with torch.inference_mode():
            for inicio in range(0, len(textos), _BATCH_SIZE):
                entradas = tokenizador(
                    list(textos[inicio : inicio + _BATCH_SIZE]),
                    padding=True,
                    truncation=True,
                    max_length=MAX_SEQUENCE_LENGTH,
                    return_tensors="pt",
                )
                estados = modelo(**entradas).last_hidden_state
                mascara = entradas["attention_mask"].unsqueeze(-1)
                vetores = (estados * mascara).sum(dim=1) / mascara.sum(dim=1).clamp(
                    min=1
                )
                lotes.append(vetores.cpu().numpy())

        return normalize(np.vstack(lotes)).astype(np.float32)

    @property
    def _bert(self):
        if self._encoder is None:
            repositorio = os.getenv(BERT_MODEL_ENV, DEFAULT_BERT_MODEL)
            revisao = _bert_revision()

            from transformers import AutoModel, AutoTokenizer

            tokenizador = AutoTokenizer.from_pretrained(
                repositorio,
                revision=revisao,
            )
            modelo = AutoModel.from_pretrained(
                repositorio,
                revision=revisao,
            )
            modelo.eval()
            self._encoder = (modelo, tokenizador)
        return self._encoder


@lru_cache(maxsize=1)
def _catalogo() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _fluxo_da_macro(macro: str) -> str:
    entrada = _catalogo().get(macro)
    return entrada["fluxo"] if entrada else LIMITATION_FLOW


@lru_cache(maxsize=1)
def get_classifier() -> ClassificadorDeIntencoes:
    """Instância compartilhada, para os artefatos serem carregados uma só vez."""

    return ClassificadorDeIntencoes()


def classify(texto: str, top_k: int = 3) -> Classificacao:
    """Atalho para a instância compartilhada."""

    return get_classifier().classify(texto, top_k=top_k)
