"""Correcoes de instrumentacao expostas pela campanha de RNF05 de 22/09/2026.

Tres falhas, cada uma escondendo informacao que a medicao precisava:

1. o duplo do cenario negativo reconhecia comparacao por palavra-chave e deixava
   passar um dos quatro prompts, atrasando so parte das requisicoes;
2. o cliente do LLM repetia chamadas sem registrar nada, entao um travamento do
   provedor aparecia apenas como uma requisicao lenta, sem causa verificavel;
3. o adaptador do OpenRouter nao olhava o motivo de parada, e respostas cortadas
   pelo limite de tokens eram entregues como se estivessem completas.
"""

import importlib
import io
import json
import logging
import sys
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request

import pytest

import app.pipeline as pipeline
from app.gemini import client
from app.tests.performance.prompts import COMPARACOES, CONSULTAS_SIMPLES

MODULO_DO_DUPLO = "app.tests.performance.api_com_atraso"


@pytest.fixture
def duplo():
    """Importa o duplo e desfaz a troca que ele faz no pipeline ao ser importado.

    O modulo substitui `app.pipeline.generate_chat_response` em nivel de modulo.
    Sem restaurar, a troca vazaria para o resto da suite e qualquer teste
    posterior com prompt de comparacao dormiria 25 s.
    """

    original = pipeline.generate_chat_response
    sys.modules.pop(MODULO_DO_DUPLO, None)
    modulo = importlib.import_module(MODULO_DO_DUPLO)
    try:
        yield modulo
    finally:
        pipeline.generate_chat_response = original
        sys.modules.pop(MODULO_DO_DUPLO, None)


class RespostaFalsa:
    def __init__(self, corpo: dict) -> None:
        self.corpo = corpo

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.corpo).encode("utf-8")


class TestDuploDeterministico:
    @pytest.mark.parametrize("pedido", COMPARACOES)
    def test_todo_pedido_de_comparacao_recebe_o_atraso(self, duplo, monkeypatch, pedido):
        """Inclui o prompt que a versao por palavra-chave deixava passar."""

        esperas = []
        monkeypatch.setattr(duplo, "sleep", esperas.append)
        monkeypatch.setattr(duplo, "_original", lambda request, *a, **k: "resposta")

        duplo._com_atraso(SimpleNamespace(message=pedido))

        assert esperas == [duplo.ATRASO_SEGUNDOS]

    @pytest.mark.parametrize("pedido", CONSULTAS_SIMPLES)
    def test_consulta_simples_segue_sem_atraso(self, duplo, monkeypatch, pedido):
        esperas = []
        monkeypatch.setattr(duplo, "sleep", esperas.append)
        monkeypatch.setattr(duplo, "_original", lambda request, *a, **k: "resposta")

        duplo._com_atraso(SimpleNamespace(message=pedido))

        assert esperas == []

    def test_prompt_que_escapava_do_duplo_antigo(self, duplo):
        """Regressao explicita do caso que falhou na rodada de 22/09/2026."""

        escapava = "Entre o PRJ-0442 e o PRJ-0518, qual esta mais proximo do prazo planejado?"

        assert escapava in duplo.PEDIDOS_DE_COMPARACAO

    def test_fixture_restaura_o_pipeline(self, duplo):
        assert pipeline.generate_chat_response is duplo._com_atraso


def test_pipeline_voltou_ao_original_depois_do_duplo():
    """Roda depois dos testes do duplo e confirma que a troca nao vazou."""

    assert getattr(pipeline.generate_chat_response, "__name__", "") != "_com_atraso"


class TestNovaTentativaRegistrada:
    def test_cada_nova_tentativa_gera_aviso(self, monkeypatch, caplog):
        monkeypatch.setenv("GEMINI_MAX_RETRIES", "2")
        monkeypatch.setattr(client, "sleep", lambda _s: None)
        respostas = iter(
            [
                HTTPError("https://x", 503, "high demand", {}, io.BytesIO(b"{}")),
                RespostaFalsa({"ok": True}),
            ]
        )

        def urlopen_falso(_requisicao, timeout):
            proxima = next(respostas)
            if isinstance(proxima, Exception):
                raise proxima
            return proxima

        monkeypatch.setattr(client, "urlopen", urlopen_falso)

        with caplog.at_level(logging.WARNING, logger=client.logger.name):
            client._send_request_with_retry(Request("https://x", data=b"{}"))

        assert "HTTP 503" in caplog.text
        assert "tentativa 2 de 3" in caplog.text

    def test_timeout_tambem_e_registrado(self, monkeypatch, caplog):
        """O caso suspeito do outlier de 37,7 s: timeout seguido de sucesso."""

        monkeypatch.setenv("GEMINI_MAX_RETRIES", "1")
        monkeypatch.setattr(client, "sleep", lambda _s: None)
        chamadas = []

        def urlopen_falso(_requisicao, timeout):
            chamadas.append(timeout)
            if len(chamadas) == 1:
                raise TimeoutError("read timed out")
            return RespostaFalsa({"ok": True})

        monkeypatch.setattr(client, "urlopen", urlopen_falso)

        with caplog.at_level(logging.WARNING, logger=client.logger.name):
            client._send_request_with_retry(Request("https://x", data=b"{}"))

        assert "TimeoutError" in caplog.text

    def test_sucesso_direto_nao_gera_aviso(self, monkeypatch, caplog):
        monkeypatch.setattr(client, "urlopen", lambda _r, timeout: RespostaFalsa({}))

        with caplog.at_level(logging.WARNING, logger=client.logger.name):
            client._send_request_with_retry(Request("https://x", data=b"{}"))

        assert caplog.text == ""


class TestTruncamentoVisivel:
    def _resposta(self, finish_reason: str) -> dict:
        return {
            "model": "google/gemini-3.7-flash",
            "choices": [
                {
                    "finish_reason": finish_reason,
                    "message": {"content": "o contexto nao e suficiente para"},
                }
            ],
            "usage": {"completion_tokens": 512},
        }

    def test_resposta_cortada_pelo_limite_gera_aviso(self, monkeypatch, caplog):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setattr(
            client, "urlopen", lambda _r, timeout: RespostaFalsa(self._resposta("length"))
        )

        with caplog.at_level(logging.WARNING, logger=client.logger.name):
            client._call_llm("prompt", api_key="k")

        assert "truncada" in caplog.text

    def test_resposta_completa_nao_gera_aviso(self, monkeypatch, caplog):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setattr(
            client, "urlopen", lambda _r, timeout: RespostaFalsa(self._resposta("stop"))
        )

        with caplog.at_level(logging.WARNING, logger=client.logger.name):
            client._call_llm("prompt", api_key="k")

        assert "truncada" not in caplog.text
