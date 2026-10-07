"""Alteracao pelo chat pela API: chat, previa, confirmacao, desfazer e historico.

Usa o servico com repositorio em memoria e prova que o caminho da escrita nao
chama o provedor de linguagem em nenhum momento.
"""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.data_changes.service import set_data_change_service
from app.main import app
from app.security import get_access_context
from app.tests.data_change_support import (
    ACTIVITY_LOTE2,
    PRJ_0442,
    Clock,
    build_repository,
    build_service,
    consulta,
    gerente,
    pmo,
)


@pytest.fixture()
def api(monkeypatch):
    clock = Clock()
    repo = build_repository()
    service = build_service(repo, clock)
    set_data_change_service(service)

    calls = []

    def provider_must_not_run(*args, **kwargs):
        calls.append(args)
        raise AssertionError("A alteracao pelo chat nao pode chamar o provedor de linguagem.")

    monkeypatch.setattr("app.pipeline.generate_chat_response", provider_must_not_run)
    current = {"context": gerente()}
    app.dependency_overrides[get_access_context] = lambda: current["context"]
    try:
        yield TestClient(app), repo, clock, current, calls
    finally:
        app.dependency_overrides.pop(get_access_context, None)
        set_data_change_service(None)


def chat(client, message):
    return client.post(
        "/api/chat",
        json={"message": message, "conversation_id": "conversa-s5-06", "use_intent_classifier": False},
    )


def test_fluxo_completo_pelo_chat_confirma_e_desfaz(api):
    client, repo, clock, _current, calls = api

    response = chat(client, "Prorroga o prazo do PRJ-0442 para 31/03/2027")
    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "alteracao-dados-chat"
    assert body["data_change"]["status"] == "preview"
    preview = body["data_change"]["preview"]
    assert preview["before"] == {"value": "2026-12-20", "display": "20/12/2026"}
    assert preview["after"] == {"value": "2027-03-31", "display": "31/03/2027"}
    assert "Nada foi gravado ainda" in body["text"]
    assert repo.state.targets["projeto"][PRJ_0442].values["planned_end_date"] == date(2026, 12, 20)

    confirmed = client.post(
        f"/api/data-change-previews/{preview['pending_change_id']}/confirm",
        json={"reason": "Replanejamento aprovado"},
    )
    assert confirmed.status_code == 200
    change = confirmed.json()
    assert change["status"] == "aplicada"
    assert repo.state.targets["projeto"][PRJ_0442].values["planned_end_date"] == date(2027, 3, 31)

    history = client.get("/api/data-changes", params={"project_code": "PRJ-0442", "field": "projeto.prazo_final"})
    assert history.status_code == 200
    assert history.json()["items"][0]["can_undo"] is True

    clock.advance(minutes=5)
    undone = client.post(f"/api/data-changes/{change['change_id']}/undo")
    assert undone.status_code == 200
    assert undone.json()["restored"]["display"] == "20/12/2026"
    assert repo.state.targets["projeto"][PRJ_0442].values["planned_end_date"] == date(2026, 12, 20)
    assert calls == []


def test_pmo_recebe_recusa_no_chat_e_nada_e_gravado(api):
    client, repo, _clock, current, calls = api
    current["context"] = pmo()

    response = chat(client, "Prorroga o prazo do PRJ-0442 para 31/03/2027")

    assert response.status_code == 200
    data_change = response.json()["data_change"]
    assert data_change["status"] == "rejected"
    assert data_change["code"] == "OUT_OF_SCOPE_FOR_PROFILE"
    assert repo.state.pending == {}
    assert [e.event_type for e in repo.state.audit] == ["authorization.access_denied"]
    assert calls == []


def test_consulta_nao_ve_projeto_fora_do_escopo_de_leitura(api):
    client, _repo, _clock, current, _calls = api
    current["context"] = consulta()
    # A leitura do PRJ-0442 ja e negada antes do pipeline (S5-04).
    assert chat(client, "Prorroga o prazo do PRJ-0442 para 31/03/2027").status_code == 403


def test_rotas_do_cartao_devolvem_os_codigos_do_contrato(api):
    client, _repo, clock, current, _calls = api
    preview = chat(client, "Prorroga o prazo do PRJ-0442 para 31/03/2027").json()["data_change"]["preview"]
    pending_id = preview["pending_change_id"]

    current["context"] = pmo()
    assert client.post(f"/api/data-change-previews/{pending_id}/confirm").json()["error"]["code"] == "PREVIEW_NOT_FOUND"

    current["context"] = gerente()
    assert client.post("/api/data-change-previews/nao-e-uuid/confirm").status_code == 404
    clock.advance(minutes=11)
    expired = client.post(f"/api/data-change-previews/{pending_id}/confirm")
    assert (expired.status_code, expired.json()["error"]["code"]) == (410, "PREVIEW_EXPIRED")

    invalid = client.post(f"/api/data-change-previews/{pending_id}/confirm", json={"reason": "x" * 501})
    assert (invalid.status_code, invalid.json()["error"]["code"]) == (422, "DATA_CHANGE_INVALID_INPUT")


def test_rota_de_previa_cria_a_previa_com_alvo_escolhido(api):
    client, _repo, _clock, current, _calls = api
    response = client.post(
        "/api/data-change-previews",
        json={"project_code": "PRJ-0442", "field": "cronograma.progresso", "target_id": ACTIVITY_LOTE2, "raw_value": "70"},
    )
    assert response.status_code == 200
    assert response.json()["preview"]["after"]["display"] == "70%"

    invalid = client.post(
        "/api/data-change-previews",
        json={"project_code": "PRJ-0442", "field": "cronograma.progresso", "target_id": ACTIVITY_LOTE2, "raw_value": "140"},
    )
    assert (invalid.status_code, invalid.json()["error"]["code"]) == (422, "INVALID_VALUE")

    malformed = client.post(
        "/api/data-change-previews",
        json={"project_code": "PRJ-0442", "field": "cronograma.progresso", "target_id": "abc", "raw_value": "70"},
    )
    assert (malformed.status_code, malformed.json()["error"]["code"]) == (404, "TARGET_NOT_FOUND")

    mismatch = client.post(
        "/api/data-change-previews",
        json={"project_code": "PRJ-0442", "entity": "risco", "field": "cronograma.progresso",
              "target_id": ACTIVITY_LOTE2, "raw_value": "70"},
    )
    assert (mismatch.status_code, mismatch.json()["error"]["code"]) == (422, "DATA_CHANGE_INVALID_INPUT")

    current["context"] = pmo()
    denied = client.post(
        "/api/data-change-previews",
        json={"project_code": "PRJ-0442", "field": "projeto.status", "raw_value": "critico"},
    )
    assert (denied.status_code, denied.json()["error"]["code"]) == (403, "OUT_OF_SCOPE_FOR_PROFILE")


def test_sem_banco_a_alteracao_fica_indisponivel_sem_fingir_gravacao(monkeypatch):
    set_data_change_service(None)
    app.dependency_overrides[get_access_context] = gerente
    monkeypatch.setattr(
        "app.pipeline.generate_chat_response",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("sem provedor")),
    )
    try:
        client = TestClient(app)
        response = chat(client, "Prorroga o prazo do PRJ-0442 para 31/03/2027")
        assert response.status_code == 200
        assert response.json()["data_change"]["code"] == "DATA_CHANGE_UNAVAILABLE"
        route = client.post("/api/data-changes/00000000-0000-4000-8000-000000000001/undo")
        assert (route.status_code, route.json()["error"]["code"]) == (503, "DATA_CHANGE_UNAVAILABLE")
    finally:
        app.dependency_overrides.pop(get_access_context, None)


def test_mensagem_com_dado_sensivel_continua_bloqueada_antes_da_alteracao(api):
    client, repo, _clock, _current, _calls = api
    response = chat(
        client,
        "Muda o responsável do risco Interferência com a operação comercial do PRJ-0442 para fulano@metro.sp.gov.br",
    )
    assert response.json()["model"] == "bloqueio-dado-sensivel"
    assert repo.state.pending == {}


def test_intencao_de_atualizacao_sem_pedido_reconhecivel_recebe_orientacao(api, monkeypatch):
    client, _repo, _clock, _current, calls = api
    from types import SimpleNamespace

    resultado = SimpleNamespace(
        macrointencao="TRANSACAO",
        intencao="transacao_atualizar_cronograma",
        confianca_macro=0.9,
        confianca_intencao=0.8,
        roteada=True,
        fluxo="Executor de Transacao -> Confirmacao -> Registro",
        handler="handler:transacao_atualizar_cronograma",
        alternativas=[],
    )
    monkeypatch.setattr("app.nlp.inference.classify", lambda message: resultado)
    response = client.post("/api/chat", json={"message": "quero replanejar o cronograma do PRJ-0442"})

    body = response.json()
    assert body["data_change"]["status"] == "needs_input"
    assert "Prorroga o prazo do PRJ-0442" in body["text"]
    assert calls == []


@pytest.mark.parametrize("value", ["-10%", "1000%", "35,555%"])
def test_regressao_progresso_invalido_pela_api_nao_cria_previa_nem_grava(api, value):
    """Reproducao da revisao do MR da #260, pelo chat e pela rota do cartao."""

    client, repo, _clock, _current, calls = api
    response = chat(
        client,
        f"Atualiza o progresso da atividade Instalação do lote 2 de equipamentos de sinalização do PRJ-0442 para {value}",
    )

    assert response.status_code == 200
    data_change = response.json()["data_change"]
    assert (data_change["status"], data_change["code"]) == ("rejected", "INVALID_VALUE")
    assert data_change["preview"] is None
    assert repo.state.pending == {}

    route = client.post(
        "/api/data-change-previews",
        json={"project_code": "PRJ-0442", "field": "cronograma.progresso",
              "target_id": ACTIVITY_LOTE2, "raw_value": value},
    )
    assert (route.status_code, route.json()["error"]["code"]) == (422, "INVALID_VALUE")
    assert repo.state.pending == {}
    assert repo.state.change_records == {}
    assert str(repo.state.targets["cronograma"][ACTIVITY_LOTE2].values["progress_percent"]) == "35.00"
    assert calls == []
