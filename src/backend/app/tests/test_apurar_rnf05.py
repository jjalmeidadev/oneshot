"""Regras do protocolo revisado do RNF05, aplicadas por `apurar_rnf05.py`.

O caso que motivou a revisao esta reproduzido em
`test_linha_de_base_da_sprint_4_seria_inconclusiva`: 10 amostras comparativas,
uma delas de 37,7 s. Pelo protocolo antigo a rodada reprovou, porque o "P95"
com 10 amostras e a pior requisicao. Pelo revisado, a mesma rodada nao aprova
nem reprova: ela precisa ser estendida.
"""

import csv

import pytest

from app.tests.performance.apurar_rnf05 import (
    AMOSTRA_MINIMA,
    APROVADO,
    INCONCLUSIVO,
    REPROVADO,
    apurar_rota,
    ler_csv,
    veredito_geral,
)


def _csv(tmp_path, nome_rodada, linhas):
    pasta = tmp_path / nome_rodada
    pasta.mkdir()
    caminho = pasta / f"rnf05-{nome_rodada}_stats.csv"
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=["Type", "Name", "Request Count", "Failure Count", "95%"]
        )
        escritor.writeheader()
        for nome, amostras, falhas, p95 in linhas:
            escritor.writerow(
                {"Type": "POST", "Name": nome, "Request Count": amostras,
                 "Failure Count": falhas, "95%": p95}
            )
        escritor.writerow(
            {"Type": "", "Name": "Aggregated", "Request Count": 0, "Failure Count": 0, "95%": 0}
        )
    return caminho


class TestOrdemDasVerificacoes:
    def test_erro_reprova_mesmo_com_amostra_pequena(self):
        """Zero erro nao e criterio estatistico: um erro basta."""

        resultado = apurar_rota("baseline", "simples", 5, 1, 3_000)

        assert resultado.veredito == REPROVADO

    def test_amostra_insuficiente_e_inconclusiva_mesmo_acima_do_teto(self):
        """Com poucas amostras o "P95" e o maximo: nao sustenta reprovacao."""

        resultado = apurar_rota("baseline", "comparacao", 10, 0, 38_000)

        assert resultado.veredito == INCONCLUSIVO

    def test_amostra_insuficiente_tambem_nao_aprova(self):
        resultado = apurar_rota("baseline", "comparacao", 10, 0, 7_000)

        assert resultado.veredito == INCONCLUSIVO

    def test_amostra_minima_exata_ja_e_apurada(self):
        assert apurar_rota("b", "simples", AMOSTRA_MINIMA, 0, 9_000).veredito == APROVADO

    @pytest.mark.parametrize(
        ("rota", "p95", "esperado"),
        [
            ("simples", 10_000, APROVADO),
            ("simples", 10_001, REPROVADO),
            ("comparacao", 20_000, APROVADO),
            ("comparacao", 20_001, REPROVADO),
        ],
    )
    def test_tetos_do_requisito_inalterados(self, rota, p95, esperado):
        """A revisao mudou o protocolo, nao os tetos de 10 s e 20 s."""

        assert apurar_rota("carga", rota, 100, 0, p95).veredito == esperado


class TestLeituraDoCsv:
    def test_linha_de_base_da_sprint_4_seria_inconclusiva(self, tmp_path):
        caminho = _csv(
            tmp_path,
            "baseline",
            [("POST /api/chat [simples]", 24, 0, 6_600), ("POST /api/chat [comparacao]", 10, 0, 38_000)],
        )

        resultados = ler_csv(caminho)

        por_rota = {r.rota: r.veredito for r in resultados}
        assert por_rota == {"simples": INCONCLUSIVO, "comparacao": INCONCLUSIVO}
        assert veredito_geral(resultados) == INCONCLUSIVO

    def test_carga_da_sprint_4_seria_aprovada(self, tmp_path):
        caminho = _csv(
            tmp_path,
            "carga",
            [("POST /api/chat [simples]", 165, 0, 7_100), ("POST /api/chat [comparacao]", 43, 0, 8_000)],
        )

        assert veredito_geral(ler_csv(caminho)) == APROVADO

    def test_rota_ausente_nao_passa_em_silencio(self, tmp_path):
        """Uma rodada sem nenhuma comparacao nao mediu a rota comparativa."""

        caminho = _csv(tmp_path, "violacao", [("POST /api/chat [simples]", 80, 0, 5_000)])

        resultados = ler_csv(caminho)

        comparacao = next(r for r in resultados if r.rota == "comparacao")
        assert comparacao.amostras == 0
        assert comparacao.veredito == INCONCLUSIVO

    def test_linha_agregada_e_ignorada(self, tmp_path):
        caminho = _csv(
            tmp_path,
            "carga",
            [("POST /api/chat [simples]", 50, 0, 5_000), ("POST /api/chat [comparacao]", 50, 0, 6_000)],
        )

        assert {r.rota for r in ler_csv(caminho)} == {"simples", "comparacao"}


class TestVereditoGeral:
    def test_reprovado_prevalece_sobre_inconclusivo(self):
        resultados = [
            apurar_rota("a", "simples", 10, 0, 1_000),
            apurar_rota("b", "comparacao", 100, 0, 25_000),
        ]

        assert veredito_geral(resultados) == REPROVADO

    def test_atendido_so_com_todas_as_rotas_aprovadas(self):
        resultados = [
            apurar_rota("baseline", "simples", 60, 0, 6_000),
            apurar_rota("baseline", "comparacao", 40, 0, 9_000),
            apurar_rota("carga", "simples", 200, 0, 7_000),
            apurar_rota("carga", "comparacao", 50, 0, 8_000),
        ]

        assert veredito_geral(resultados) == APROVADO

    def test_lista_vazia_e_inconclusiva(self):
        assert veredito_geral([]) == INCONCLUSIVO
