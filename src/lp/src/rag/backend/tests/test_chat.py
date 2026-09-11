"""Chat: recusa honesta sem modelo, e registro da interação na sala."""

from __future__ import annotations

import pytest

from app.dependencies import get_model
from app.model.client import ModelAnswer, RagModelError
from app.schemas import ChatSource


class ModeloFalso:
    """Fica no lugar do RAG enquanto ele não existe."""

    name = "falso"

    def __init__(self, sources: list[ChatSource] | None = None) -> None:
        self.sources = sources or []
        self.perguntas: list[str] = []

    async def answer(self, question: str, previous_interaction_id: str | None = None):
        self.perguntas.append(question)
        return ModelAnswer(
            text=f"Resposta para: {question}",
            model="falso",
            interaction_id="interacao-1",
            sources=self.sources,
        )


class ModeloQuebrado:
    name = "quebrado"

    async def answer(self, question: str, previous_interaction_id: str | None = None):
        raise RagModelError("O modelo caiu.", status_code=502)


def test_sem_modelo_configurado_o_chat_responde_503(client):
    resposta = client.post("/api/chat", json={"message": "Qual o status do portfólio?"})
    assert resposta.status_code == 503
    assert "não está configurado" in resposta.json()["detail"]


def test_pergunta_vazia_e_recusada(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422


def test_resposta_do_modelo_entra_na_sala(client):
    from app.main import app

    modelo = ModeloFalso()
    app.dependency_overrides[get_model] = lambda: modelo

    session_id = client.post("/api/live/sessions", json={"name": "Ana"}).json()["id"]
    resposta = client.post(
        "/api/chat", json={"session_id": session_id, "message": "Tem marco atrasado?"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["text"] == "Resposta para: Tem marco atrasado?"
    assert corpo["interaction_id"] == "interacao-1"

    # O que interessa: a conversa ficou visível para quem observa.
    sessao = client.get("/api/live/sessions").json()["sessions"][0]
    assert [(m["role"], m["content"]) for m in sessao["messages"]] == [
        ("user", "Tem marco atrasado?"),
        ("assistant", "Resposta para: Tem marco atrasado?"),
    ]
    assert sessao["status"] == "idle"


def test_chat_sem_sessao_funciona_mas_nao_e_observavel(client):
    from app.main import app

    app.dependency_overrides[get_model] = lambda: ModeloFalso()

    assert client.post("/api/chat", json={"message": "Olá"}).status_code == 200
    assert client.get("/api/live/sessions").json()["sessions"] == []


def test_sessao_desconhecida_e_404(client):
    from app.main import app

    app.dependency_overrides[get_model] = lambda: ModeloFalso()

    resposta = client.post(
        "/api/chat", json={"session_id": "fantasma", "message": "Olá"}
    )
    assert resposta.status_code == 404


def test_falha_do_modelo_nao_deixa_a_sessao_presa_em_pensando(client):
    from app.main import app

    app.dependency_overrides[get_model] = lambda: ModeloQuebrado()

    session_id = client.post("/api/live/sessions", json={}).json()["id"]
    assert client.post(
        "/api/chat", json={"session_id": session_id, "message": "Olá"}
    ).status_code == 502

    sessao = client.get("/api/live/sessions").json()["sessions"][0]
    assert sessao["status"] == "idle"
    # A pergunta continua registrada — a falha foi na resposta, não na pergunta.
    assert [m["role"] for m in sessao["messages"]] == ["user"]


@pytest.mark.parametrize("com_arquivo", [True, False])
def test_fonte_ganha_link_de_download_quando_o_arquivo_existe(
    client, documents_dir, com_arquivo
):
    from app.main import app

    if com_arquivo:
        (documents_dir / "TAP.pdf").write_bytes(b"%PDF-1.4 conteudo")

    app.dependency_overrides[get_model] = lambda: ModeloFalso(
        sources=[ChatSource(id="s1", title="TAP do Portfólio XPTO", document="TAP.pdf")]
    )

    fonte = client.post("/api/chat", json={"message": "De onde veio?"}).json()["sources"][0]
    if com_arquivo:
        assert fonte["download_url"].startswith("/api/documents/")
        assert client.get(fonte["download_url"]).status_code == 200
    else:
        assert fonte["download_url"] is None
