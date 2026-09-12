"""O caminho completo, sem tocar na rede."""

from __future__ import annotations

import asyncio

from helpers import indice_de_teste

from model.config import ModelSettings
from model.generator import GenerationResult
from model.pipeline import RagPipeline


class GeradorFalso:
    """Guarda o que recebeu, para o teste conferir o que foi ao modelo."""

    def __init__(self, texto: str = "Resposta [Fonte 1].") -> None:
        self.texto = texto
        self.hits = None
        self.previous = "não recebido"

    async def __call__(self, question, hits, settings, previous_interaction_id):
        self.hits = hits
        self.previous = previous_interaction_id
        return GenerationResult(text=self.texto, model="falso", interaction_id="interacao-1")


def pipeline(vetor, gerador, **ajustes):
    async def embed(textos, settings):
        return [vetor]

    return RagPipeline(
        settings=ModelSettings(api_key="x", **ajustes),
        index=indice_de_teste(),
        embed=embed,
        generator=gerador,
    )


def test_a_resposta_traz_as_fontes_recuperadas():
    gerador = GeradorFalso()
    resposta = asyncio.run(
        pipeline([0.9, 0.4, 0.0], gerador, top_k=2, min_score=0.0).answer("E aí?")
    )

    assert resposta.text == "Resposta [Fonte 1]."
    assert resposta.model == "falso"
    assert resposta.interaction_id == "interacao-1"
    assert [f.title for f in resposta.sources] == ["Riscos", "Cronograma"]
    assert resposta.sources[0].document == "Projeto.md"


def test_a_ordem_das_fontes_acompanha_a_numeracao_do_prompt():
    gerador = GeradorFalso()
    resposta = asyncio.run(
        pipeline([0.1, 0.9, 0.0], gerador, top_k=3, min_score=0.0).answer("E aí?")
    )

    # [Fonte N] no texto precisa bater com sources[N-1]; se a lista fosse
    # reordenada ou deduplicada aqui, a citação apontaria para o documento
    # errado.
    assert [h.chunk.section for h in gerador.hits] == [f.title for f in resposta.sources]


def test_nada_acima_do_piso_gera_resposta_sem_fontes():
    gerador = GeradorFalso(texto="Não encontrei isso na documentação.")
    resposta = asyncio.run(
        pipeline([0.4, 0.4, 0.4], gerador, top_k=3, min_score=0.9).answer("E aí?")
    )

    assert resposta.sources == []
    assert gerador.hits == []


def test_o_encadeamento_de_turnos_e_repassado():
    gerador = GeradorFalso()
    asyncio.run(
        pipeline([1.0, 0.0, 0.0], gerador, min_score=0.0).answer("E aí?", "anterior-9")
    )
    assert gerador.previous == "anterior-9"


def test_o_trecho_da_fonte_e_recortado():
    gerador = GeradorFalso()
    resposta = asyncio.run(
        pipeline([1.0, 0.0, 0.0], gerador, top_k=1, min_score=0.0).answer("E aí?")
    )
    fonte = resposta.sources[0]
    assert fonte.excerpt.startswith("Conteúdo de Riscos")
    assert "\n" not in fonte.excerpt
    assert 0 < fonte.score <= 1
