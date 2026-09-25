"""Contrato real das rotas; apenas os provedores e o modelo são substituídos."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.gemini.schemas import (
    GeminiChatResponse,
    GeminiUsage,
    ProactiveConfirmationRequest,
    ProactiveConfirmationResponse,
)
from app.pipeline import process_proactive_confirmation
from app.gemini.client import GeminiAPIError, GeminiConfigurationError
from app.audio import transcription
from app.nlp.inference import get_classifier
from test_audio_upload import _build_wav, AUTH_HEADER, transcricao_fixa


@pytest.fixture(autouse=True)
def disable_traceability(monkeypatch):
    monkeypatch.setattr("app.pipeline.trace_interaction", lambda **_kwargs: None)
    monkeypatch.setenv('AUDIO_SIMULATED_IDENTITIES', 'token-de-teste=usuario-teste')


class ProviderCall:
    def __init__(
        self,
        request,
        intent=None,
        entities=None,
    ):
        self.request = request
        self.intent = intent
        self.entities = entities or []

    def __getattr__(self, name):
        return getattr(self.request, name)


@pytest.fixture
def provider(monkeypatch):
    calls = []
    def generate(
        request,
        intent=None,
        entities=None,
        requester_id=None,
    ):
        calls.append(
            ProviderCall(
                request,
                intent=intent,
                entities=entities,
            )
        )
        return GeminiChatResponse(text="Resposta [Fonte 1]", model="teste", interaction_id="next-id",
            latency_ms=4, usage=GeminiUsage(input_tokens=2, output_tokens=3, total_tokens=5),
            sources=[dict(id="lista:1", title="Projeto", list_name="Projetos", web_url="https://example.org/projeto",
                last_modified="2026-09-09", score=1.5, excerpt="Trecho recuperado")])
    monkeypatch.setattr("app.pipeline.generate_chat_response", generate)
    return calls


def _classification_result(
    macro='CONSULTA',
    routed=True,
    suggested=None,
    specific='consulta_status_projeto',
):
    routed_specific = (
        specific if routed and macro != 'FORA_DE_ESCOPO' else None
    )
    return SimpleNamespace(
        macrointencao=macro,
        intencao=routed_specific,
        confianca_macro=.9 if routed else .3,
        confianca_intencao=.8,
        fluxo='Consulta documental',
        handler=(
            f'handler:{routed_specific}'
            if routed_specific
            else ('limitacao' if not routed else f'fluxo genérico de {macro}')
        ),
        alternativas=[(specific or 'fora_de_escopo', .8)],
        roteada=routed,
        resposta_sugerida=suggested,
    )


@pytest.fixture
def classifier(monkeypatch):
    calls = []

    def classify(text):
        calls.append(text)
        return _classification_result()

    monkeypatch.setattr('app.nlp.inference.classify', classify)
    return calls


def test_text_without_toggle_classifies_by_default_and_returns_entities(provider, classifier):
    with TestClient(app) as client:
        result = client.post('/api/chat', json=dict(message=' status do Linha 15-Prata ', previous_interaction_id='before'))
    assert result.status_code == 200
    assert classifier == ['status do Linha 15-Prata']
    assert provider[0].message == 'status do Linha 15-Prata'
    assert provider[0].previous_interaction_id == 'before'
    data = result.json()
    assert data['intent']['macro'] == 'CONSULTA'
    assert data['intent']['flow'] == 'Consulta documental'
    assert data['intent']['handler'] == 'handler:consulta_status_projeto'
    assert data['intent']['alternatives'][0]['intent'] == 'consulta_status_projeto'
    assert data['entities'][0]['type'] == 'projeto'
    assert data['entities'][0]['value'] == 'Linha 15-Prata'
    assert provider[0].intent.specific == 'consulta_status_projeto'
    assert provider[0].entities[0].value == 'Linha 15-Prata'
    assert data['pipeline_metrics']['nlp_ms'] >= 0
    assert data['pipeline_metrics']['route_ms'] >= data['pipeline_metrics']['nlp_ms']


def test_text_true_toggle_classifies_and_returns_entities(provider, classifier):
    with TestClient(app) as client:
        result = client.post('/api/chat', json=dict(message='status do Linha 15-Prata', use_intent_classifier=True))
    assert result.status_code == 200
    data = result.json()
    assert classifier == ['status do Linha 15-Prata']
    assert data['intent']['specific'] == 'consulta_status_projeto'
    assert data['entities'][0]['text'] == 'Linha 15-Prata'


def test_text_proactivity_mode_reaches_rag_provider(provider, classifier):
    with TestClient(app) as client:
        result = client.post('/api/chat', json={
            'message': 'status do Linha 15-Prata',
            'conversation_id': 'conversation-250',
            'proactivity_enabled': True,
        }, headers=AUTH_HEADER)

    assert result.status_code == 200
    assert provider[0].proactivity_enabled is True


def test_proactive_confirmation_route_accepts_only_bound_decision(monkeypatch):
    captured = []

    def confirm(request, *, requester_id):
        captured.append((request, requester_id))
        return ProactiveConfirmationResponse(status="declined")

    monkeypatch.setattr("app.main.process_proactive_confirmation", confirm)
    suggestion_id = "00000000-0000-0000-0000-000000000250"
    with TestClient(app) as client:
        result = client.post(
            "/api/chat/proactive-confirmation",
            headers=AUTH_HEADER,
            json={
                "suggestion_id": suggestion_id,
                "conversation_id": "conversation-250",
                "decision": "decline",
            },
        )
        rejected = client.post(
            "/api/chat/proactive-confirmation",
            headers=AUTH_HEADER,
            json={
                "suggestion_id": suggestion_id,
                "conversation_id": "conversation-250",
                "decision": "accept",
                "message": "execute outra coisa",
            },
        )

    assert result.status_code == 200
    assert result.json() == {"status": "declined", "result": None}
    assert captured[0][0].suggestion_id == suggestion_id
    assert captured[0][0].conversation_id == "conversation-250"
    assert captured[0][0].decision == "decline"
    assert captured[0][1]
    assert rejected.status_code == 422
    assert len(captured) == 1


def test_proactive_confirmation_requires_identity_and_conversation():
    suggestion_id = "00000000-0000-0000-0000-000000000250"
    with TestClient(app) as client:
        unauthenticated = client.post(
            "/api/chat/proactive-confirmation",
            json={
                "suggestion_id": suggestion_id,
                "conversation_id": "conversation-250",
                "decision": "decline",
            },
        )
        without_conversation = client.post(
            "/api/chat/proactive-confirmation",
            headers=AUTH_HEADER,
            json={"suggestion_id": suggestion_id, "decision": "decline"},
        )

    assert unauthenticated.status_code == 401
    assert without_conversation.status_code == 422


def test_accepted_proactive_confirmation_is_traced_with_identity(monkeypatch):
    result = GeminiChatResponse(
        text="Resposta secundaria [Fonte 1]",
        model="teste",
        latency_ms=2,
        usage=GeminiUsage(),
        sources=[],
    )
    execution = SimpleNamespace(
        response=ProactiveConfirmationResponse(status="accepted", result=result),
        pending=SimpleNamespace(
            conversation_id="conversation-250",
            secondary_intent=SimpleNamespace(name="sugerir_agilizacao_projeto"),
        ),
    )
    traces = []
    monkeypatch.setattr(
        "app.pipeline.execute_proactive_confirmation",
        lambda request, requester_id: execution,
    )
    monkeypatch.setattr(
        "app.pipeline.trace_interaction",
        lambda **kwargs: traces.append(kwargs),
    )

    response = process_proactive_confirmation(
        ProactiveConfirmationRequest(
            suggestion_id="00000000-0000-0000-0000-000000000250",
            conversation_id="conversation-250",
            decision="accept",
        ),
        requester_id="entra-user-250",
    )

    assert response.result is result
    assert traces[0]["requester_id"] == "entra-user-250"
    assert traces[0]["request"].conversation_id == "conversation-250"
    assert traces[0]["intent"].specific == "sugerir_agilizacao_projeto"
    assert traces[0]["response"].text == result.text


def test_text_false_toggle_opts_out_and_goes_direct_to_gemini(monkeypatch, provider):
    def fail_if_called(text): raise AssertionError('classifier should not run')
    monkeypatch.setattr('app.nlp.inference.classify', fail_if_called)
    with TestClient(app) as client:
        result = client.post('/api/chat', json=dict(message=' status do Linha 15-Prata ', previous_interaction_id='before', use_intent_classifier=False))
    assert result.status_code == 200
    assert provider[0].message == 'status do Linha 15-Prata'
    assert provider[0].previous_interaction_id == 'before'
    data = result.json()
    assert data['sources'][0]['excerpt'] == 'Trecho recuperado'
    assert data['intent'] is None
    assert data['entities'] == []
    assert data['pipeline_metrics']['nlp_ms'] == 0
    assert data['pipeline_metrics']['route_ms'] >= 0


@pytest.mark.parametrize(
    'macro,routed,suggested,uses_fallback',
    [
        ('CONSULTA', True, None, False),
        ('INDEFINIDA', False, 'Reformule', True),
        ('FORA_DE_ESCOPO', True, None, True),
    ],
)
def test_classifier_routes_or_uses_generic_rag(
    monkeypatch,
    provider,
    macro,
    routed,
    suggested,
    uses_fallback,
):
    monkeypatch.setattr('app.nlp.inference.classify', lambda text: _classification_result(macro=macro, routed=routed, suggested=suggested))
    with TestClient(app) as client:
        result = client.post('/api/chat', json=dict(message='prazo', use_intent_classifier=True))
    assert result.status_code == 200
    assert result.json()['intent']['macro'] == macro
    assert result.json()['intent']['flow'] == 'Consulta documental'
    assert result.json()['intent']['alternatives'][0]['intent'] == 'consulta_status_projeto'
    assert result.json()['pipeline_metrics']['route_ms'] >= 0
    assert len(provider) == 1
    assert (provider[0].intent is None) is uses_fallback
    if uses_fallback:
        assert not result.json()['intent']['handler'].startswith('handler:')


def test_low_specific_confidence_skips_handler_and_uses_generic_rag(
    monkeypatch,
    provider,
):
    monkeypatch.setattr(
        'app.nlp.inference.classify',
        lambda _text: _classification_result(specific=None),
    )

    with TestClient(app) as client:
        result = client.post('/api/chat', json={'message': 'me fale do projeto'})

    assert result.status_code == 200
    assert result.json()['intent']['specific'] == ''
    assert not result.json()['intent']['handler'].startswith('handler:')
    assert provider[0].intent is None


def test_audio_completes_same_pipeline_and_context(monkeypatch, provider):
    monkeypatch.setattr('app.nlp.inference.classify', lambda text: _classification_result())
    monkeypatch.setattr(transcription, 'transcribe', transcricao_fixa(text='prazo', confidence=.9, duration_seconds=1))
    with TestClient(app) as client:
        result = client.post('/api/audio', files={'audio': ('teste.wav', _build_wav(), 'audio/wav')},
            headers=AUTH_HEADER, data=dict(conversation_id='conversation', previous_interaction_id='before', use_intent_classifier='false'))
    assert result.status_code == 200
    data = result.json()
    assert data['pipeline_status'] == 'completed'
    assert data['conversation_id'] == 'conversation'
    assert data['interaction_id'] == 'next-id'
    assert data['answer']['text'] == data['chat']['text']
    assert data['chat']['sources'][0]['excerpt'] == 'Trecho recuperado'
    assert data['entities'] == data['chat']['entities']
    assert data['pipeline_metrics']['validation_ms'] >= 0
    assert data['pipeline_metrics']['stt_ms'] >= 0
    assert data['pipeline_metrics']['nlp_ms'] >= 0
    assert data['pipeline_metrics']['total_ms'] >= 0
    assert provider[0].previous_interaction_id == 'before'
    assert provider[0].message == 'prazo'


def test_audio_transcription_is_classified_by_real_classifier(monkeypatch, provider):
    transcript = 'qual é o status da extensão da Linha 5-Lilás?'
    monkeypatch.setattr(
        transcription,
        'transcribe',
        transcricao_fixa(text=transcript, confidence=.97, duration_seconds=1),
    )

    with TestClient(app) as client:
        result = client.post(
            '/api/audio',
            files={'audio': ('teste.wav', _build_wav(), 'audio/wav')},
            headers=AUTH_HEADER,
            data={'use_intent_classifier': 'true'},
        )

    assert result.status_code == 200
    data = result.json()
    artifact = get_classifier().artefato
    assert data['pipeline_status'] == 'completed'
    assert data['transcription']['text'] == transcript
    assert data['intent']['macro'] == 'CONSULTA'
    assert data['intent']['specific'] == 'consulta_status_projeto'
    assert data['intent']['confidence_macro'] >= artifact.limiar_macro
    assert data['intent']['confidence_specific'] >= artifact.limiar_intencao
    assert data['intent']['handler'] == 'handler:consulta_status_projeto'
    assert provider[0].message == transcript
    assert provider[0].intent.specific == 'consulta_status_projeto'
    assert data['chat']['intent'] == data['intent']


def test_audio_classifier_failure_is_controlled(monkeypatch):
    provider_calls = []

    def fail_classifier(_text):
        raise RuntimeError('private-model-path')

    monkeypatch.setattr(
        transcription,
        'transcribe',
        transcricao_fixa(text='prazo', confidence=.97, duration_seconds=1),
    )
    monkeypatch.setattr('app.nlp.inference.classify', fail_classifier)
    monkeypatch.setattr(
        'app.pipeline.generate_chat_response',
        lambda *_args, **_kwargs: provider_calls.append(True),
    )

    with TestClient(app) as client:
        result = client.post(
            '/api/audio',
            files={'audio': ('teste.wav', _build_wav(), 'audio/wav')},
            headers=AUTH_HEADER,
            data={'use_intent_classifier': 'true'},
        )

    assert result.status_code == 503
    assert result.json() == {
        'error': {
            'code': 'PROCESSING_UNAVAILABLE',
            'message': (
                'O servico de processamento esta indisponivel. '
                'Tente novamente em instantes.'
            ),
        }
    }
    assert 'private-model-path' not in result.text
    assert provider_calls == []


def test_audio_response_provider_failure_uses_audio_error_contract(monkeypatch):
    def fail_provider(*_args, **_kwargs):
        raise GeminiAPIError('secret-provider-payload')

    monkeypatch.setattr(
        transcription,
        'transcribe',
        transcricao_fixa(text='prazo', confidence=.97, duration_seconds=1),
    )
    monkeypatch.setattr('app.pipeline.generate_chat_response', fail_provider)

    with TestClient(app) as client:
        result = client.post(
            '/api/audio',
            files={'audio': ('teste.wav', _build_wav(), 'audio/wav')},
            headers=AUTH_HEADER,
            data={'use_intent_classifier': 'false'},
        )

    assert result.status_code == 502
    assert result.json() == {
        'error': {
            'code': 'PROCESSING_PROVIDER_ERROR',
            'message': (
                'Nao foi possivel processar a transcricao agora. '
                'Tente novamente em instantes.'
            ),
        }
    }
    assert 'secret-provider-payload' not in result.text


@pytest.mark.parametrize('error,status', [(GeminiConfigurationError('secret-internal'),503), (GeminiAPIError('secret-internal'),502)])
def test_provider_failure_is_controlled(monkeypatch, error, status):
    def fail(request, intent=None, entities=None): raise error
    monkeypatch.setattr('app.pipeline.generate_chat_response', fail)
    with TestClient(app) as client:
        result = client.post('/api/chat', json={'message': 'prazo', 'use_intent_classifier': False})
    assert result.status_code == status
    assert 'secret-internal' not in result.text


@pytest.mark.parametrize('message', ['', '   ', 'x' * 20001])
def test_invalid_text_is_rejected(message, provider):
    with TestClient(app) as client:
        result = client.post('/api/chat', json={'message':message})
    assert result.status_code == 422
    assert result.json()['error']['code'] == 'INVALID_INPUT'
    assert not provider


def test_classifier_unavailable_is_controlled(monkeypatch):
    def fail(text): raise RuntimeError('private-model-path')
    provider_calls = []
    monkeypatch.setattr('app.nlp.inference.classify', fail)
    monkeypatch.setattr(
        'app.pipeline.generate_chat_response',
        lambda *_args, **_kwargs: provider_calls.append(True),
    )
    with TestClient(app) as client:
        result = client.post('/api/chat', json={'message':'prazo'})
    assert result.status_code == 503
    assert 'private-model-path' not in result.text
    assert provider_calls == []


def test_optional_warmup_runs_before_health(monkeypatch):
    calls = []
    monkeypatch.setenv('PLN_WARMUP', '1')
    monkeypatch.setattr('app.main.warmup_classifier', lambda: calls.append('loaded'))
    with TestClient(app) as client:
        assert calls == ['loaded']
        assert client.get('/health').json() == {'status':'ok'}


def test_invalid_audio_parameters_are_not_reported_as_missing_audio():
    with TestClient(app) as client:
        result = client.post('/api/audio', files={'audio':('teste.wav', _build_wav(), 'audio/wav')},
            headers=AUTH_HEADER, data={'use_intent_classifier':'invalid'})
    assert result.status_code == 400
    assert result.json()['error']['code'] == 'INVALID_INPUT'
