"""O canal WebSocket entrega a sala no instante em que ela muda."""

from __future__ import annotations


def test_conexao_recebe_a_sala_atual(client):
    client.post("/api/live/sessions", json={"name": "Ana"})

    with client.websocket_connect("/ws/live") as ws:
        evento = ws.receive_json()

    assert evento["type"] == "snapshot"
    assert [s["name"] for s in evento["sessions"]] == ["Ana"]


def test_entrada_e_mensagem_chegam_sem_polling(client):
    from app.dependencies import get_model
    from app.main import app
    from tests.test_chat import ModeloFalso

    app.dependency_overrides[get_model] = lambda: ModeloFalso()

    with client.websocket_connect("/ws/live") as ws:
        assert ws.receive_json()["sessions"] == []

        session_id = client.post("/api/live/sessions", json={"name": "Bruno"}).json()["id"]
        entrada = ws.receive_json()
        assert entrada["type"] == "sessions"
        assert [s["name"] for s in entrada["sessions"]] == ["Bruno"]

        client.post("/api/chat", json={"session_id": session_id, "message": "Olá"})

        # Duas escritas na sala: a pergunta e a resposta.
        pergunta = ws.receive_json()
        assert pergunta["sessions"][0]["status"] == "thinking"
        assert pergunta["sessions"][0]["messages"][-1]["content"] == "Olá"

        resposta = ws.receive_json()
        assert resposta["sessions"][0]["status"] == "idle"
        assert resposta["sessions"][0]["messages"][-1]["role"] == "assistant"
        # O contrato do WebSocket é o mesmo do polling, camelCase incluído.
        assert "lastSeen" in resposta["sessions"][0]
