"""Contrato da presença ao vivo — o que a LP consome."""

from __future__ import annotations

import asyncio

from app.config import Settings
from app.live.store import LiveStore


def test_health_reporta_modelo_nao_configurado(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["model"] == "não configurado"
    assert body["live_sessions"] == 0


def test_sessao_entra_com_os_campos_que_o_frontend_espera(client):
    created = client.post("/api/live/sessions", json={"name": "Felipe"})
    assert created.status_code == 201

    session = created.json()
    # Estes nomes são lidos por `useLivePresence.ts` e pelo cartão de presença.
    assert set(session) == {"id", "name", "color", "status", "lastSeen", "messages"}
    assert session["name"] == "Felipe"
    assert session["status"] == "idle"
    assert session["messages"] == []
    # Milissegundos, como `Date.now()`: em segundos isto seria ~1.7e9.
    assert session["lastSeen"] > 1_000_000_000_000


def test_sem_nome_o_servidor_batiza_o_visitante(client):
    session = client.post("/api/live/sessions", json={}).json()
    assert session["name"] == "Convidado 1"
    assert session["color"].startswith("#")


def test_listagem_devolve_a_sala_inteira(client):
    client.post("/api/live/sessions", json={"name": "Ana"})
    client.post("/api/live/sessions", json={"name": "Bruno"})

    body = client.get("/api/live/sessions").json()
    assert [session["name"] for session in body["sessions"]] == ["Ana", "Bruno"]


def test_heartbeat_atualiza_o_estado_exibido(client):
    session_id = client.post("/api/live/sessions", json={}).json()["id"]

    updated = client.post(
        f"/api/live/sessions/{session_id}/heartbeat", json={"status": "typing"}
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "typing"


def test_heartbeat_de_sessao_inexistente_e_404(client):
    assert client.post("/api/live/sessions/nao-existe/heartbeat", json={}).status_code == 404


def test_saida_remove_da_sala(client):
    session_id = client.post("/api/live/sessions", json={}).json()["id"]

    assert client.delete(f"/api/live/sessions/{session_id}").status_code == 204
    assert client.get("/api/live/sessions").json()["sessions"] == []


def test_sala_cheia_recusa_novas_sessoes(client):
    from app.config import get_settings

    for _ in range(get_settings().max_sessions):
        assert client.post("/api/live/sessions", json={}).status_code == 201

    recusada = client.post("/api/live/sessions", json={})
    assert recusada.status_code == 503
    assert "cheia" in recusada.json()["detail"]


# --- Testes diretos do store, sem passar por HTTP -------------------------


def test_store_expira_sessao_sem_sinal_de_vida():
    store = LiveStore(Settings(session_ttl_seconds=0))

    async def cenario() -> list[str]:
        await store.join("Ana")
        await asyncio.sleep(0.01)
        return await store.sweep()

    expiradas = asyncio.run(cenario())
    assert len(expiradas) == 1
    assert asyncio.run(store.snapshot()) == []


def test_store_descarta_as_mensagens_mais_antigas():
    store = LiveStore(Settings(max_messages_per_session=2))

    async def cenario():
        session = await store.join("Ana")
        for texto in ("um", "dois", "três"):
            await store.append_message(session.id, "user", texto)
        return await store.get(session.id)

    session = asyncio.run(cenario())
    assert [message.content for message in session.messages] == ["dois", "três"]


def test_store_avisa_os_inscritos_a_cada_mudanca():
    store = LiveStore(Settings())
    recebidos: list[int] = []

    async def ouvinte(sessions):
        recebidos.append(len(sessions))

    async def cenario():
        store.subscribe(ouvinte)
        session = await store.join("Ana")
        await store.append_message(session.id, "user", "olá")
        await store.leave(session.id)

    asyncio.run(cenario())
    assert recebidos == [1, 1, 0]
