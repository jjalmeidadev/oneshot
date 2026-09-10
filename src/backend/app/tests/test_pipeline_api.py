"""Contrato real das rotas; apenas os provedores e o modelo são substituídos."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.gemini.schemas import GeminiChatResponse, GeminiUsage
from app.gemini.client import GeminiAPIError, GeminiConfigurationError
from app.audio import transcription
from test_audio_upload import _build_wav, AUTH_HEADER, transcricao_fixa


@pytest.fixture
def provider(monkeypatch):
    calls = []
    def generate(request):
        calls.append(request)
        return GeminiChatResponse(text="Resposta [Fonte 1]", model="teste", interaction_id="next-id",
            latency_ms=4, usage=GeminiUsage(input_tokens=2, output_tokens=3, total_tokens=5),
            sources=[dict(id="lista:1", title="Projeto", list_name="Projetos", web_url="https://example.org/projeto",
                last_modified="2026-09-09", score=1.5, excerpt="Trecho recuperado")])
    monkeypatch.setattr("app.pipeline.generate_chat_response", generate)
    return calls


def test_text_keeps_context_toggle_and_sources(provider):
    with TestClient(app) as client:
        result = client.post('/api/chat', json=dict(message=' prazo ', previous_interaction_id='before', use_intent_classifier=False))
    assert result.status_code == 200
    assert provider[0].message == 'prazo'
    assert provider[0].previous_interaction_id == 'before'
    assert result.json()['sources'][0]['excerpt'] == 'Trecho recuperado'
    assert result.json()['intent'] is None


@pytest.mark.parametrize('macro,routed,suggested', [('CONSULTA', True, None), ('INDEFINIDA', False, 'Reformule'), ('FORA_DE_ESCOPO', True, None)])
def test_classifier_routes_or_limits(monkeypatch, provider, macro, routed, suggested):
    monkeypatch.setattr('app.nlp.inference.classify', lambda text: SimpleNamespace(
        macrointencao=macro, intencao='consulta_status_projeto' if routed else None,
        confianca_macro=.9 if routed else .3, confianca_intencao=.8,
        roteada=routed, resposta_sugerida=suggested))
    with TestClient(app) as client:
        result = client.post('/api/chat', json=dict(message='prazo', use_intent_classifier=True))
    assert result.status_code == 200
    assert result.json()['intent']['macro'] == macro
    assert bool(provider) == (macro == 'CONSULTA')
    if macro != 'CONSULTA':
        assert result.json()['interaction_id'] is None
        assert result.json()['sources'] == []


def test_audio_completes_same_pipeline_and_context(monkeypatch, provider):
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
    assert provider[0].previous_interaction_id == 'before'
    assert provider[0].message == 'prazo'


@pytest.mark.parametrize('error,status', [(GeminiConfigurationError('secret-internal'),503), (GeminiAPIError('secret-internal'),502)])
def test_provider_failure_is_controlled(monkeypatch, error, status):
    def fail(request): raise error
    monkeypatch.setattr('app.pipeline.generate_chat_response', fail)
    with TestClient(app) as client:
        result = client.post('/api/chat', json={'message': 'prazo'})
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
    monkeypatch.setattr('app.nlp.inference.classify', fail)
    with TestClient(app) as client:
        result = client.post('/api/chat', json={'message':'prazo', 'use_intent_classifier':True})
    assert result.status_code == 503
    assert 'private-model-path' not in result.text


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
