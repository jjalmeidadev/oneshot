"""Regressões da #282: consultas curtas, status e limite de agendamento."""

import pytest

from app.nlp.inference import Classificacao, LIMITATION_ANSWER
from app.nlp.routing import apply_domain_routes, SCHEDULING_LIMITATION_HANDLER


def prediction(text, *, macro="INDEFINIDA", specific=None):
    return Classificacao(
        texto=text, macrointencao=macro, intencao=specific,
        confianca_macro=0.42, confianca_intencao=0.31,
        fluxo="fluxo original", handler="handler original",
        alternativas=[("consulta_status_projeto", 0.31)],
        resposta_sugerida=LIMITATION_ANSWER,
    )


@pytest.mark.parametrize("text", [
    "fale sobre os Objetos perdidos", "fale sobre o Bilhete digital",
    "Bilhete digital", "BILHETE DIGITAL?", "Como funciona o bilhete digital?",
    "Me explique sobre os objetos perdidos", "achados e perdidos",
    "Preciso de informações sobre o Bilhete digital", "O que é o bilhete digital?",
])
def test_operational_topics_route_to_document_retrieval(text):
    original = prediction(text)
    result = apply_domain_routes(original)
    assert result.macrointencao == "CONSULTA"
    assert result.intencao is None
    assert result.roteada
    assert result.resposta_sugerida is None
    assert result.confianca_macro == original.confianca_macro
    assert result.alternativas == original.alternativas


@pytest.mark.parametrize("text", [
    "Mostre o status do projeto PRJ-0442", "Qual é o status do projeto XPTO?",
    "Exiba o andamento da Linha 5-Lilás", "Informe a situação do portfólio",
    "Me mostre o status do projeto PRJ-9999",
])
def test_status_paraphrases_select_consultation_instead_of_update(text):
    result = apply_domain_routes(prediction(text, macro="CONSULTA"))
    assert result.intencao == "consulta_status_projeto"
    assert result.handler == "handler:consulta_status_projeto"


@pytest.mark.parametrize("text", [
    "Reserve uma sala de reunião para amanhã", "Agende uma reunião amanhã",
    "Marque um compromisso para sexta", "Reserve uma sala para o projeto PRJ-0442",
])
def test_generic_scheduling_and_room_reservations_are_rejected(text):
    result = apply_domain_routes(prediction(
        text, macro="TRANSACAO", specific="transacao_agendar_compromisso",
    ))
    assert result.macrointencao == "FORA_DE_ESCOPO"
    assert result.intencao is None
    assert result.handler == SCHEDULING_LIMITATION_HANDLER
    assert "reservas de salas" in result.resposta_sugerida


@pytest.mark.parametrize("text", [
    "Agende uma reunião de acompanhamento do projeto PRJ-0442",
    "Marque uma revisão de portfólio amanhã", "Agende um checkpoint da Linha 5-Lilás",
])
def test_scheduling_with_portfolio_scope_keeps_model_decision(text):
    original = prediction(text, macro="TRANSACAO", specific="transacao_agendar_compromisso")
    assert apply_domain_routes(original) == original


@pytest.mark.parametrize("text", [
    "Atualize o status do projeto PRJ-0442", "Não mostre o status do projeto PRJ-0442",
    "Mostre o status do projeto PRJ-0442 e atualize para concluído",
    "Mostre o status do clima", "Qual é a previsão do tempo?",
    "Cancele o Bilhete digital", "Bilhete digital e reserve uma sala",
    "Não quero informações sobre o Bilhete digital", "bom dia, tudo certo?",
])
def test_other_requests_are_not_promoted_to_consultation(text):
    original = prediction(text)
    assert apply_domain_routes(original).macrointencao != "CONSULTA"


def test_reformulation_offers_topic_example_without_requiring_project():
    assert "indicando o tema" in LIMITATION_ANSWER
    assert "Como funciona o Bilhete digital?" in LIMITATION_ANSWER
    assert "indicando o projeto" not in LIMITATION_ANSWER


def test_pipeline_blocks_reservation_without_calling_provider_and_traces(monkeypatch):
    from app.gemini.schemas import GeminiChatRequest
    from app.pipeline import process_message

    calls = []
    result = apply_domain_routes(prediction(
        "Reserve uma sala de reunião para amanhã", macro="TRANSACAO",
        specific="transacao_agendar_compromisso",
    ))
    monkeypatch.setattr("app.nlp.inference.classify", lambda text: result)
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr("app.pipeline.generate_chat_response", lambda *a, **k: pytest.fail("Reserva enviada ao provedor"))
    response = process_message(GeminiChatRequest(message=result.texto))
    assert response.intent.macro == "FORA_DE_ESCOPO"
    assert response.intent.specific == ""
    assert response.sources == []
    assert response.usage.total_tokens == 0
    assert response.text == result.resposta_sugerida
    assert len(calls) == 1
    assert calls[0]["response"] is response
