"""Cache e ritmo — a parte que faz um lote longo sobreviver ao limite de taxa."""

from __future__ import annotations

import asyncio
import json
import time

import httpx
import numpy as np
import pytest

from model.config import ModelSettings
from model.embeddings import (
    EmbeddingCache,
    EmbeddingError,
    Throttle,
    _cache_key,
    _extract_values,
    _retry_delay,
    embed_one,
    embed_texts,
)


def ajustes(**extras) -> ModelSettings:
    return ModelSettings(api_key="chave", **extras)


# --- Leitura da resposta --------------------------------------------------


def test_aceita_as_duas_formas_de_resposta():
    assert _extract_values({"embedding": {"values": [1.0, 2.0]}}) == [1.0, 2.0]
    assert _extract_values({"embeddings": [{"values": [3.0]}]}) == [3.0]


def test_resposta_sem_vetor_e_erro():
    with pytest.raises(EmbeddingError):
        _extract_values({"nada": "aqui"})


def test_le_o_tempo_de_espera_sugerido_pela_api():
    resposta = httpx.Response(
        429,
        json={"error": {"details": [{"retryDelay": "31s"}]}},
        request=httpx.Request("POST", "http://x"),
    )
    assert _retry_delay(resposta) == 31.0


def test_cabecalho_retry_after_tem_precedencia():
    resposta = httpx.Response(
        429, headers={"retry-after": "12"}, request=httpx.Request("POST", "http://x")
    )
    assert _retry_delay(resposta) == 12.0


# --- Cache ----------------------------------------------------------------


def test_o_cache_sobrevive_entre_execucoes(tmp_path):
    cache = EmbeddingCache(tmp_path)
    cache.put("chave-a", [0.1, 0.2])
    cache.flush()

    outro = EmbeddingCache(tmp_path)
    assert len(outro) == 1
    assert outro.get("chave-a") == pytest.approx([0.1, 0.2])
    assert outro.get("inexistente") is None


def test_cache_inconsistente_e_descartado_em_vez_de_quebrar(tmp_path):
    cache = EmbeddingCache(tmp_path)
    cache.put("chave-a", [0.1])
    cache.flush()
    # Um arquivo com mais chaves que vetores: o cache é economia, nunca fonte
    # de verdade, então ele se descarta em silêncio.
    (tmp_path / "embedding-cache.json").write_text(json.dumps(["a", "b"]), encoding="utf-8")

    assert len(EmbeddingCache(tmp_path)) == 0


def test_a_chave_muda_com_o_texto_e_com_o_modelo():
    a = _cache_key("texto", ajustes())
    assert a == _cache_key("texto", ajustes())
    assert a != _cache_key("outro texto", ajustes())
    assert a != _cache_key("texto", ajustes(embedding_dimensions=1536))


def test_o_que_esta_no_cache_nao_e_pedido_de_novo(tmp_path):
    cache = EmbeddingCache(tmp_path)
    settings = ajustes()
    cache.put(_cache_key("já vetorizado", settings), [9.0, 9.0])

    chamadas = []

    def responder(request: httpx.Request) -> httpx.Response:
        chamadas.append(request)
        return httpx.Response(200, json={"embedding": {"values": [1.0, 1.0]}})

    async def cenario():
        import model.embeddings as modulo

        original = modulo.httpx.AsyncClient

        def cliente(*args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(responder)
            return original(*args, **kwargs)

        modulo.httpx.AsyncClient = cliente
        try:
            return await embed_texts(["já vetorizado", "novo"], settings, cache=cache)
        finally:
            modulo.httpx.AsyncClient = original

    vetores = asyncio.run(cenario())

    assert vetores[0] == pytest.approx([9.0, 9.0])
    assert vetores[1] == pytest.approx([1.0, 1.0])
    # Só o trecho novo foi pedido à API.
    assert len(chamadas) == 1


# --- Ritmo ----------------------------------------------------------------


def test_o_throttle_espaca_as_chamadas():
    async def cenario():
        throttle = Throttle(requests_per_minute=600)  # 0,1s entre chamadas
        comeco = time.monotonic()
        for _ in range(3):
            await throttle.acquire()
        return time.monotonic() - comeco

    # Três chamadas com 0,1s de intervalo levam pelo menos 0,2s.
    assert asyncio.run(cenario()) >= 0.18


def test_o_429_desacelera_o_lote_inteiro():
    async def cenario():
        throttle = Throttle(requests_per_minute=600)
        intervalo_antes = throttle.interval
        await throttle.back_off(0.01)
        return intervalo_antes, throttle.interval

    antes, depois = asyncio.run(cenario())
    assert depois > antes


def test_erro_nao_repetivel_falha_na_hora():
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "pedido inválido"}})

    async def cenario():
        async with httpx.AsyncClient(transport=httpx.MockTransport(responder)) as client:
            return await embed_one(client, "texto", ajustes())

    with pytest.raises(EmbeddingError) as erro:
        asyncio.run(cenario())
    # 400 não é limite de taxa: repetir seria só perder tempo.
    assert erro.value.status_code == 400
