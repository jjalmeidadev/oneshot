"""Extracao de entidades do dominio do portfolio (Secao 3.1.2 do Projeto.md)."""

import json

import pytest

from app.nlp.entities import LEXICON_PATH, Entidade, extract_entities


def tipos_e_valores(texto: str) -> list[tuple[str, str]]:
    return [(e.tipo, e.valor) for e in extract_entities(texto)]


class TestLexiconEntities:
    @pytest.mark.parametrize(
        ("texto", "esperado"),
        [
            pytest.param(
                "qual é o status do Linha 15-Prata?",
                ("projeto", "Linha 15-Prata"),
                id="projeto",
            ),
            pytest.param(
                "projetos do subportfólio de Expansão",
                ("subportfolio", "subportfólio de Expansão"),
                id="subportfolio",
            ),
            pytest.param(
                "o que mudou no último trimestre",
                ("periodo", "no último trimestre"),
                id="periodo",
            ),
            pytest.param(
                "quem é o patrocinador",
                ("responsavel", "o patrocinador"),
                id="responsavel",
            ),
            pytest.param(
                "me mostra a matriz de riscos",
                ("documento", "matriz de riscos"),
                id="documento",
            ),
            pytest.param("qual o SPI atual", ("indicador", "SPI"), id="indicador"),
            pytest.param(
                "projetos em homologação",
                ("status", "em homologação"),
                id="status",
            ),
            pytest.param(
                "risco de estouro de orçamento",
                ("risco", "estouro de orçamento"),
                id="risco",
            ),
            pytest.param(
                "me avise semanalmente", ("frequencia", "semanalmente"), id="frequencia"
            ),
            pytest.param("me avise no Teams", ("canal", "no Teams"), id="canal"),
        ],
    )
    def test_extracts_each_domain_type(
        self, texto: str, esperado: tuple[str, str]
    ) -> None:
        assert esperado in tipos_e_valores(texto)

    def test_recognises_the_pilot_document_of_the_mvp(self) -> None:
        """O Mapa de Beneficios e o documento piloto das transacoes (Secao 2.7).

        Ele nao aparece no conjunto sintetico, mas e nomeado no escopo macro do
        TAPI, entao precisa estar no lexico.
        """

        assert ("documento", "mapa de benefícios") in tipos_e_valores(
            "preciso atualizar o Mapa de Benefícios do Linha 4-Amarela"
        )

    def test_returns_nothing_for_text_without_domain_terms(self) -> None:
        assert extract_entities("qual a previsão do tempo para amanhã") == []

    def test_returns_nothing_for_empty_text(self) -> None:
        assert extract_entities("") == []


class TestSurfaceRobustness:
    """As variacoes do conjunto sintetico incluem caixa e remocao de acento."""

    @pytest.mark.parametrize(
        "texto",
        [
            pytest.param("qual é o status da modernização da Linha 3-Vermelha?", id="base"),
            pytest.param("QUAL É O STATUS DA MODERNIZAÇÃO DA LINHA 3-VERMELHA?", id="maiusculas"),
            pytest.param("qual e o status da modernizacao da Linha 3-Vermelha?", id="sem-acento"),
            pytest.param("PFV QUAL E O STATUS DA MODERNIZACAO DA LINHA 3-VERMELHA", id="cortesia"),
        ],
    )
    def test_resolves_surface_variants_to_the_canonical_value(self, texto: str) -> None:
        projetos = [e.valor for e in extract_entities(texto) if e.tipo == "projeto"]

        assert projetos == ["modernização da Linha 3-Vermelha"]

    def test_surface_form_is_preserved_alongside_the_canonical_value(self) -> None:
        (entidade,) = [
            e for e in extract_entities("status do LINHA 17-OURO") if e.tipo == "projeto"
        ]

        assert entidade.texto == "LINHA 17-OURO"
        assert entidade.valor == "Linha 17-Ouro"


class TestPatternEntities:
    """Padroes generalizam para valores que o lexico nao conhece."""

    @pytest.mark.parametrize(
        ("texto", "tipo", "valor"),
        [
            pytest.param("status do PRJ-9999", "projeto", "PRJ-9999", id="codigo-novo"),
            pytest.param("o SPI caiu 42%", "percentual", "42%", id="percentual"),
            pytest.param("entrega em 01/12/2028", "data", "01/12/2028", id="data"),
            pytest.param("atraso de 45 dias", "prazo_dias", "45 dias", id="prazo"),
        ],
    )
    def test_extracts_values_outside_the_lexicon(
        self, texto: str, tipo: str, valor: str
    ) -> None:
        assert (tipo, valor) in tipos_e_valores(texto)

    def test_does_not_treat_a_short_acronym_as_a_project_code(self) -> None:
        assert extract_entities("ok-123") == []


class TestOverlapResolution:
    def test_longest_term_wins(self) -> None:
        """"extensão da Linha 5-Lilás" e o projeto, nao "Linha 5-Lilás"."""

        projetos = [
            e.valor
            for e in extract_entities("status da extensão da Linha 5-Lilás")
            if e.tipo == "projeto"
        ]

        assert projetos == ["extensão da Linha 5-Lilás"]

    def test_entities_never_overlap_and_come_in_reading_order(self) -> None:
        entidades = extract_entities(
            "compare o Linha 2-Verde e o PRJ-2031 por custo no acumulado do ano"
        )

        assert entidades == sorted(entidades, key=lambda e: e.inicio)
        for anterior, seguinte in zip(entidades, entidades[1:]):
            assert anterior.fim <= seguinte.inicio

    def test_offsets_point_back_to_the_original_text(self) -> None:
        texto = "ranking do subportfólio de Expansão por avanço físico"

        for entidade in extract_entities(texto):
            assert texto[entidade.inicio : entidade.fim] == entidade.texto


class TestAmbiguousTerms:
    """O extrator nao decide o que depende da intencao."""

    def test_term_belonging_to_two_types_reports_both(self) -> None:
        (entidade,) = [
            e
            for e in extract_entities("compare os projetos por aderência ao cronograma")
            if e.ambigua
        ]

        assert set(entidade.tipos) == {"criterio", "indicador"}
        assert entidade.tipo in entidade.tipos

    def test_unambiguous_term_reports_a_single_type(self) -> None:
        (entidade,) = [e for e in extract_entities("por custo") if e.tipo == "criterio"]

        assert entidade.tipos == ("criterio",)
        assert not entidade.ambigua


class TestLexiconFile:
    def test_every_type_declares_description_and_terms(self) -> None:
        tipos = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))["tipos"]

        assert tipos
        for nome, definicao in tipos.items():
            assert definicao["descricao"].endswith("."), nome
            assert definicao["termos"], nome
            assert len(set(definicao["termos"])) == len(definicao["termos"]), nome

    def test_entity_defaults_its_type_list_from_the_single_type(self) -> None:
        entidade = Entidade(
            tipo="projeto", valor="Linha 2-Verde", texto="Linha 2-Verde", inicio=0, fim=13
        )

        assert entidade.tipos == ("projeto",)
