"""O adaptador que roda o modelo RAG dentro deste processo."""

from __future__ import annotations

import asyncio

import pytest

from app.config import Settings
from app.model import local as adaptador
from app.model.client import RagModelError, RagModelNotConfigured, build_model


class FonteFalsa:
    def __init__(self, titulo: str) -> None:
        self.id = "s1"
        self.title = titulo
        self.document = "Projeto.md"
        self.anchor = "secao"
        self.excerpt = "Trecho recuperado."
        self.score = 0.83


class RespostaFalsa:
    def __init__(self) -> None:
        self.text = "Em andamento [Fonte 1]."
        self.model = "gemini-falso"
        self.interaction_id = "int-1"
        self.sources = [FonteFalsa("Riscos > R08")]
        self.retrieval_ms = 12
        self.generation_ms = 340


class IndexNotBuilt(RuntimeError):
    """Mesmo nome do erro do pacote do modelo, para exercitar a tradução."""


def pipeline_falso(erro: Exception | None = None):
    class PipelineFalso:
        async def answer(self, question, previous_interaction_id=None):
            if erro is not None:
                raise erro
            return RespostaFalsa()

    return lambda: PipelineFalso


def test_configuracao_local_escolhe_o_adaptador_local():
    modelo = build_model(Settings(model_backend="local"))
    assert isinstance(modelo, adaptador.LocalRagModel)
    assert modelo.name == "local"


def test_a_resposta_do_pipeline_vira_o_contrato_do_backend(monkeypatch):
    monkeypatch.setattr(adaptador, "_import_pipeline", pipeline_falso())
    resposta = asyncio.run(adaptador.LocalRagModel().answer("Qual o status?"))

    assert resposta.text == "Em andamento [Fonte 1]."
    assert resposta.model == "gemini-falso"
    assert resposta.interaction_id == "int-1"
    # O nome do arquivo é o que liga a fonte ao download em documentsRAG.
    assert resposta.sources[0].document == "Projeto.md"
    assert resposta.sources[0].title == "Riscos > R08"
    assert resposta.sources[0].score == 0.83


def test_indice_ausente_vira_503_e_nao_500(monkeypatch):
    monkeypatch.setattr(
        adaptador,
        "_import_pipeline",
        pipeline_falso(IndexNotBuilt("Não há índice. Rode python -m model.index")),
    )
    with pytest.raises(RagModelNotConfigured) as erro:
        asyncio.run(adaptador.LocalRagModel().answer("Qual o status?"))
    assert erro.value.status_code == 503
    assert "model.index" in str(erro.value)


def test_falha_do_gemini_preserva_o_codigo(monkeypatch):
    falha = RuntimeError("O Gemini respondeu 429.")
    falha.status_code = 429
    monkeypatch.setattr(adaptador, "_import_pipeline", pipeline_falso(falha))

    with pytest.raises(RagModelError) as erro:
        asyncio.run(adaptador.LocalRagModel().answer("Qual o status?"))
    assert erro.value.status_code == 429


def test_o_pipeline_e_construido_uma_vez_so(monkeypatch):
    construcoes = []

    class PipelineFalso:
        def __init__(self) -> None:
            construcoes.append(1)

        async def answer(self, question, previous_interaction_id=None):
            return RespostaFalsa()

    monkeypatch.setattr(adaptador, "_import_pipeline", lambda: PipelineFalso)

    modelo = adaptador.LocalRagModel()
    asyncio.run(modelo.answer("uma"))
    asyncio.run(modelo.answer("duas"))

    # Carregar o índice a cada pergunta jogaria fora o trabalho de leitura.
    assert len(construcoes) == 1
