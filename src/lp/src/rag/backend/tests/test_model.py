"""A fronteira com o modelo: escolha da implementação e caminho HTTP."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from app.config import Settings
from app.model.client import (
    HttpRagModel,
    NotConfiguredModel,
    RagModelError,
    RagModelNotConfigured,
    build_model,
)


def test_por_padrao_o_modelo_nao_esta_configurado():
    assert isinstance(build_model(Settings()), NotConfiguredModel)


def test_http_sem_url_e_configuracao_invalida():
    with pytest.raises(RagModelNotConfigured):
        build_model(Settings(model_backend="http"))


def test_http_com_url_escolhe_o_cliente_http():
    modelo = build_model(Settings(model_backend="http", model_url="http://modelo/responder"))
    assert isinstance(modelo, HttpRagModel)


def _modelo_com_resposta(handler) -> HttpRagModel:
    return HttpRagModel("http://modelo/responder", transport=httpx.MockTransport(handler))


def test_resposta_do_modelo_e_traduzida_para_o_vocabulario_do_servico():
    def responder(request: httpx.Request) -> httpx.Response:
        assert request.read().decode().find("Qual o status?") > 0
        return httpx.Response(
            200,
            json={
                "text": "Em andamento.",
                "model": "gemini-x",
                "interaction_id": "abc",
                "sources": [
                    {"id": "1", "title": "TAP", "document": "TAP.pdf", "score": 0.9}
                ],
            },
        )

    answer = asyncio.run(_modelo_com_resposta(responder).answer("Qual o status?"))
    assert answer.text == "Em andamento."
    assert answer.model == "gemini-x"
    assert answer.sources[0].document == "TAP.pdf"


def test_modelo_que_devolve_so_o_texto_ja_funciona():
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"text": "Resposta mínima."})

    answer = asyncio.run(_modelo_com_resposta(responder).answer("Olá"))
    assert answer.text == "Resposta mínima."
    assert answer.sources == []


def test_erro_do_modelo_vira_502():
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "explodiu"})

    with pytest.raises(RagModelError) as erro:
        asyncio.run(_modelo_com_resposta(responder).answer("Olá"))
    assert erro.value.status_code == 502


def test_corpo_que_nao_e_json_vira_erro_tratado():
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>não sou json</html>")

    with pytest.raises(RagModelError):
        asyncio.run(_modelo_com_resposta(responder).answer("Olá"))
