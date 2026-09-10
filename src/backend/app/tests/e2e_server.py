"""Servidor exclusivo dos testes E2E: rotas reais, provedores determinísticos.

Executar somente em localhost. Não é usado pela aplicação de produção.
"""
from types import SimpleNamespace
from time import sleep
import os

from app.main import app
from app import pipeline
from app.audio import transcription
from app.gemini.client import GeminiAPIError
from app.gemini.schemas import GeminiChatResponse, GeminiSource, GeminiUsage
from app.nlp import inference

os.environ['AUDIO_SIMULATED_IDENTITIES'] = 'e2e-token=e2e-user'


def generate(request):
    if request.message == 'falha':
        raise GeminiAPIError('detalhe privado do provedor', status_code=503)
    if request.message == 'demorada':
        sleep(2)
    return GeminiChatResponse(
        text=f'Resposta para: {request.message}. [Fonte 1]', model='provedor-de-teste',
        interaction_id='e2e-interaction', latency_ms=2, retrieval_ms=1,
        usage=GeminiUsage(input_tokens=5, output_tokens=6, total_tokens=11),
        sources=[GeminiSource(id='projetos:1', title='Projeto de teste', list_name='Projetos',
            web_url='https://example.org/projeto', last_modified='2026-09-09T12:00:00Z',
            score=1.5, excerpt='Trecho de teste: entrega em dezembro.')],
    )


def classify(text):
    return SimpleNamespace(macrointencao='CONSULTA', intencao='consulta_status_projeto',
        confianca_macro=.95, confianca_intencao=.9, roteada=True, resposta_sugerida=None)


async def transcribe(data, probe, language):
    return transcription.Transcription(text='pergunta de áudio', confidence=.95,
        duration_seconds=probe.duration_seconds)


pipeline.generate_chat_response = generate
inference.classify = classify
transcription.transcribe = transcribe
