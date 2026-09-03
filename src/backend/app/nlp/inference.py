"""Inferência do classificador de intenções.

Recebe uma solicitação em texto e devolve a macrointenção, a intenção
específica e as confianças, aplicando os dois limiares calibrados na validação
e registrados na Seção 8.10.3 do `Projeto.md`.

As transformações reproduzem **exatamente** as ajustadas no treino, na ordem em
que foram compostas. Qualquer divergência — outra tokenização, outra ordem de
blocos, normalização ausente — produz atributos que o modelo nunca viu, e o
resultado seria silenciosamente errado em vez de falhar.

A representação vencedora concatena quatro blocos: TF-IDF de palavras e de
caracteres reduzidos por SVD, o Word2Vec treinado no corpus do projeto e os
embeddings BERT congelados. Dois deles não estão no `joblib` e são carregados à
parte: o Word2Vec de `word2vec_portfolio.model` e o encoder BERT, baixado do
Hugging Face na primeira execução e mantido em cache local.

O encoder roda em **ONNX Runtime**, e não em PyTorch. O grafo exportado é o
publicado no próprio repositório do modelo, e os embeddings são idênticos aos
do `sentence-transformers` — diferença máxima de 2,4e-07, com as métricas do
conjunto de teste reproduzidas sem alteração. A troca dispensa `torch`,
`transformers` e suas dependências: o ambiente cai de 1,1 GB para cerca de
340 MB, o carregamento do encoder cai de 6,1 s para 0,33 s e some a armadilha
do wheel com CUDA no deploy em Linux. Em contrapartida, o pico de memória sobe
cerca de 240 MB.

Os limiares não são detalhe de implementação. O RNF06 exige F1-macro de 0,80 e
a intenção específica atingiu 0,7401 no teste; abaixo do limiar, a solicitação
segue para o fluxo genérico da macrointenção ou recebe resposta controlada de
limitação, em vez de acionar um handler errado. É o comportamento conservador
que o RNF04 e o RNF11 exigem.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from app.nlp.classifier import (
    ARTIFACT_DIR,
    WORD2VEC_PATH,
    ArtefatoClassificador,
    load_artifact,
)
from app.nlp.preprocessing import preprocess_text

CATALOG_PATH = ARTIFACT_DIR / "catalogo_intencoes.json"

DEFAULT_BERT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BERT_MODEL_ENV = "PLN_BERT_MODEL"
ONNX_GRAPH_FILE = "onnx/model.onnx"
TOKENIZER_FILE = "tokenizer.json"

# Identificador do preenchimento no vocabulário XLM-R usado pelo modelo. O
# `tokenizer.json` não declara o padding, e assumir o padrão 0 produziria
# identificadores diferentes dos que o encoder viu no treino.
PAD_TOKEN_ID = 1
PAD_TOKEN = "<pad>"
MAX_SEQUENCE_LENGTH = 128

UNDEFINED_MACRO = "INDEFINIDA"

_BATCH_SIZE = 64

LIMITATION_ANSWER = (
    "Não consegui identificar com segurança o que você precisa dentro do "
    "portfólio. Pode reformular indicando o projeto e a informação desejada?"
)
LIMITATION_FLOW = "Resposta padrão de limitação (RF08)"


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

    @property
    def roteada(self) -> bool:
        """A macrointenção passou do limiar e a solicitação segue no pipeline."""

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
        self._word2vec = None
        self._encoder = None
        self._idf: dict[str, float] | None = None
        self._idf_padrao: float | None = None
        self._usa_token_type_ids = False

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

        return Classificacao(
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

    def vectorize(self, textos: Sequence[str]) -> np.ndarray:
        """Aplica as mesmas transformações ajustadas no treino, na mesma ordem."""

        from sklearn.preprocessing import normalize

        textos = list(textos)
        artefato = self.artefato
        tokens = [
            preprocess_text(texto, **artefato.config_preprocessamento)
            for texto in textos
        ]

        partes = []
        for bloco in artefato.blocos_da_representacao:
            if bloco == "svd_palavra":
                bruto = artefato.svd_palavras.transform(
                    artefato.tfidf_palavras.transform(tokens)
                )
            elif bloco == "svd_char":
                # O TF-IDF de caracteres recebe o texto cru: ele modela a grafia,
                # que a tokenização e o stemming justamente descartam.
                bruto = artefato.svd_caracteres.transform(
                    artefato.tfidf_caracteres.transform(textos)
                )
            elif bloco == "w2v":
                bruto = np.vstack([self._vetor_w2v(t) for t in tokens])
            elif bloco == "bert":
                # O encoder recebe o texto cru: ele tem tokenizador próprio, e o
                # stemming aplicado aos demais blocos atrapalharia.
                bruto = self._encode(textos)
            else:
                raise ValueError(f"Bloco de representação desconhecido: {bloco}")

            partes.append(artefato.scalers[bloco].transform(normalize(bruto)))

        return np.hstack(partes) if len(partes) > 1 else partes[0]

    def _vetor_w2v(self, tokens: Sequence[str]) -> np.ndarray:
        """Média dos vetores dos tokens, ponderada pelo IDF do TF-IDF de palavras.

        Token fora do vocabulário do Word2Vec é ignorado; texto sem nenhum token
        conhecido vira o vetor nulo, como no treino.
        """

        vetores, pesos = [], []
        for token in tokens:
            if token in self.word2vec.wv:
                vetores.append(self.word2vec.wv[token])
                pesos.append(self._idf_do_token(token))

        dimensao = self.word2vec.wv.vector_size
        if not vetores:
            return np.zeros(dimensao, dtype=np.float32)

        return np.average(np.vstack(vetores), axis=0, weights=pesos).astype(np.float32)

    def _idf_do_token(self, token: str) -> float:
        if self._idf is None:
            vetorizador = self.artefato.tfidf_palavras
            self._idf = dict(
                zip(vetorizador.get_feature_names_out(), vetorizador.idf_)
            )
            self._idf_padrao = float(np.max(vetorizador.idf_))
        return self._idf.get(token, self._idf_padrao)

    @property
    def word2vec(self):
        if self._word2vec is None:
            from gensim.models import Word2Vec

            if not WORD2VEC_PATH.exists():
                raise FileNotFoundError(
                    f"Modelo Word2Vec não encontrado em {WORD2VEC_PATH}."
                )
            self._word2vec = Word2Vec.load(str(WORD2VEC_PATH))
        return self._word2vec

    def warmup(self) -> None:
        """Carrega todos os artefatos antecipadamente.

        A carga preguiçosa serve aos testes, mas em produção faria a primeira
        pessoa a usar o agente pagar o carregamento inteiro dentro da própria
        requisição. A API deve chamar isto na subida.
        """

        self.classify("aquecimento do pipeline de PLN")

    def _encode(self, textos: Sequence[str]) -> np.ndarray:
        """Embeddings do encoder congelado, com média ponderada pela máscara.

        A média sobre os tokens válidos e a normalização reproduzem o que o
        `sentence-transformers` faz com este modelo; o que muda é apenas o
        motor que executa o grafo.
        """

        sessao, tokenizador = self._bert
        lotes = []
        for inicio in range(0, len(textos), _BATCH_SIZE):
            codificados = tokenizador.encode_batch(
                list(textos[inicio : inicio + _BATCH_SIZE])
            )
            entradas = {
                "input_ids": np.array([c.ids for c in codificados], dtype=np.int64),
                "attention_mask": np.array(
                    [c.attention_mask for c in codificados], dtype=np.int64
                ),
            }
            if self._usa_token_type_ids:
                entradas["token_type_ids"] = np.zeros_like(entradas["input_ids"])

            estados = sessao.run(None, entradas)[0]
            mascara = entradas["attention_mask"][..., None].astype(np.float32)
            somas = (estados * mascara).sum(axis=1)
            vetores = somas / np.clip(mascara.sum(axis=1), 1e-9, None)
            lotes.append(vetores / np.linalg.norm(vetores, axis=1, keepdims=True))

        return np.vstack(lotes).astype(np.float32)

    @property
    def _bert(self):
        if self._encoder is None:
            import onnxruntime as ort
            from huggingface_hub import hf_hub_download
            from tokenizers import Tokenizer

            repositorio = os.getenv(BERT_MODEL_ENV, DEFAULT_BERT_MODEL)
            sessao = ort.InferenceSession(
                hf_hub_download(repositorio, ONNX_GRAPH_FILE),
                providers=["CPUExecutionProvider"],
            )
            tokenizador = Tokenizer.from_file(
                hf_hub_download(repositorio, TOKENIZER_FILE)
            )
            tokenizador.enable_padding(pad_id=PAD_TOKEN_ID, pad_token=PAD_TOKEN)
            tokenizador.enable_truncation(max_length=MAX_SEQUENCE_LENGTH)

            self._usa_token_type_ids = any(
                entrada.name == "token_type_ids" for entrada in sessao.get_inputs()
            )
            self._encoder = (sessao, tokenizador)
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
