"""Testes do coletor do RNF04, com foco na distincao entre quota e congestao.

Essa distincao nao e detalhe de implementacao: e o que separa uma rodada valida
de uma rodada perdida.

- **HTTP 429** significa quota esgotada. Cada nova tentativa consome mais uma
  unidade e devolve o mesmo erro. Repetir aqui queima o orcamento do dia sem
  obter nada — foi o que aconteceu na rodada 1, quando o retry do cliente de
  producao transformou 24 perguntas em ate 96 chamadas.
- **HTTP 502/503** e congestao passageira do provedor, nao consome quota e passa
  sozinha. Nao repetir aqui perde a pergunta a toa.

O cliente de producao (`app/gemini/client.py`) trata os dois do mesmo jeito,
porque para o usuario final ambos sao "tente de novo". Para a medicao, nao.
"""

import pytest

from app.tests.rnf04 import executar_rnf04


class RespostaFalsa:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = "erro simulado do provedor"

    def json(self) -> dict:
        return self._payload


class ClienteFalso:
    """Devolve respostas de uma fila e conta quantas chamadas recebeu."""

    def __init__(self, respostas) -> None:
        self.respostas = list(respostas)
        self.chamadas = 0

    def post(self, *_args, **_kwargs):
        self.chamadas += 1
        if not self.respostas:
            raise AssertionError("o coletor pediu mais respostas do que o previsto")
        return self.respostas.pop(0)


def _sucesso() -> RespostaFalsa:
    return RespostaFalsa(
        200,
        {
            "text": "resposta fundamentada",
            "model": "gemini-3.1-flash-lite",
            "sources": [{"id": "s1", "title": "Fonte", "list_name": "Lista"}],
            "intent": {"macro": "CONSULTA", "specific": "consulta_status_projeto"},
            "latency_ms": 900,
            "retrieval_ms": 100,
        },
    )


@pytest.fixture(autouse=True)
def sem_espera_real(monkeypatch):
    """Neutraliza o backoff para o teste nao levar dezenas de segundos."""

    monkeypatch.setattr(executar_rnf04, "sleep", lambda _segundos: None)


class TestDistincaoEntreQuotaECongestao:
    def test_congestao_e_repetida_ate_obter_resposta(self):
        cliente = ClienteFalso([RespostaFalsa(502), RespostaFalsa(502), _sucesso()])

        resultado = executar_rnf04._consulta(
            cliente, "pergunta", tentativas_transitorias=3
        )

        assert resultado["http_status"] == 200
        assert cliente.chamadas == 3
        assert resultado["tentativas"] == 3

    def test_quota_nunca_e_repetida(self):
        """O teste mais importante do arquivo.

        Repetir um 429 gasta quota para receber o mesmo 429. Se este teste
        quebrar, uma rodada inteira pode ser perdida por esgotamento.
        """

        cliente = ClienteFalso([RespostaFalsa(429), _sucesso(), _sucesso()])

        resultado = executar_rnf04._consulta(
            cliente, "pergunta", tentativas_transitorias=5
        )

        assert resultado["http_status"] == 429
        assert cliente.chamadas == 1

    def test_congestao_persistente_esgota_as_tentativas_e_desiste(self):
        cliente = ClienteFalso([RespostaFalsa(502)] * 4)

        resultado = executar_rnf04._consulta(
            cliente, "pergunta", tentativas_transitorias=3
        )

        assert resultado["http_status"] == 502
        assert cliente.chamadas == 4

    def test_sucesso_direto_nao_repete(self):
        cliente = ClienteFalso([_sucesso()])

        resultado = executar_rnf04._consulta(
            cliente, "pergunta", tentativas_transitorias=5
        )

        assert resultado["http_status"] == 200
        assert cliente.chamadas == 1
        assert resultado["tentativas"] == 1

    def test_sem_tentativas_configuradas_falha_na_primeira(self):
        cliente = ClienteFalso([RespostaFalsa(502), _sucesso()])

        resultado = executar_rnf04._consulta(cliente, "pergunta")

        assert resultado["http_status"] == 502
        assert cliente.chamadas == 1


class TestLatenciaRegistrada:
    def test_latencia_e_da_tentativa_que_respondeu(self):
        """A latencia nao pode somar as esperas entre tentativas.

        Foi essa confusao que invalidou a leitura de desempenho da rodada 1: o
        backoff entrou no cronometro e transformou ~9 s de processamento em
        39 s de "latencia" aparente.
        """

        cliente = ClienteFalso([RespostaFalsa(502), RespostaFalsa(502), _sucesso()])

        resultado = executar_rnf04._consulta(
            cliente, "pergunta", tentativas_transitorias=3, espera_base=30.0
        )

        # Com espera_base de 30 s e duas esperas, somar daria mais de 90 s.
        assert resultado["latencia_medida_ms"] < 5_000

    def test_resposta_de_sucesso_preserva_fontes_e_intencao(self):
        cliente = ClienteFalso([_sucesso()])

        resultado = executar_rnf04._consulta(cliente, "pergunta")

        assert resultado["fontes"][0]["titulo"] == "Fonte"
        assert resultado["intencao_especifica"] == "consulta_status_projeto"
        assert resultado["recuperacao_ms"] == 100
