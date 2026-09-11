"""A bancada de teste servida pelo próprio backend."""

from __future__ import annotations

from app.config import Settings


def test_pagina_da_bancada_e_servida(client):
    resposta = client.get("/teste")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    # Ela precisa falar com a API na mesma origem — sem endereço para
    # configurar no celular.
    assert "/api/live/sessions" in resposta.text
    assert "/ws/live" in resposta.text


def test_raiz_leva_para_a_bancada(client):
    resposta = client.get("/", follow_redirects=False)
    assert resposta.status_code in (307, 308)
    assert resposta.headers["location"] == "/teste"


def test_bancada_pode_ser_desligada_por_configuracao():
    # A bancada entra na sala sem autenticação: fora do desenvolvimento ela
    # precisa poder sair do ar.
    assert Settings().enable_test_bench is True
    assert Settings(enable_test_bench=False).enable_test_bench is False
