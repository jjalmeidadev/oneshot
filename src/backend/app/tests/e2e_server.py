"""Servidor exclusivo dos testes E2E: rotas reais, provedores determinísticos.

Executar somente em localhost. Não é usado pela aplicação de produção.
"""
from types import SimpleNamespace
from time import sleep
from typing import Annotated
from uuid import UUID, uuid4
import os
import json
import tempfile

from fastapi import Header, Request

# Impede que o .env sobrescreva as identidades/config simuladas definidas abaixo.
os.environ['G05_DISABLE_DOTENV_OVERRIDE'] = '1'
os.environ['AUDIO_SIMULATED_IDENTITIES'] = 'e2e-token=e2e-user'
os.environ['REPORT_SIMULATED_IDENTITIES'] = json.dumps({
    'e2e-token': {
        'subject': 'e2e-user',
        'display_name': 'Usuario E2E',
        'role': 'pmo',
        'can_export': True,
        'allow_all': True,
    }
})
os.environ['REPORT_CALLBACK_TOKEN'] = 'e2e-callback-token'
os.environ['REPORT_CONFIRMATION_SECRET'] = 'e2e-confirmation-secret'
os.environ['REPORT_REPOSITORY_MODE'] = 'memory'
os.environ['REPORT_EXECUTION_MODE'] = 'local'
os.environ['REPORT_STORAGE_MODE'] = 'local'
os.environ['REPORT_ARTIFACTS_DIR'] = os.path.join(tempfile.gettempdir(), 'g05-e2e-reports')
os.environ['PLN_WARMUP'] = '0'

from app.main import app
from app import pipeline
from app.audio import transcription
from app.gemini.client import GeminiAPIError
from app.gemini.schemas import GeminiChatResponse, GeminiSource, GeminiUsage
from app.nlp import inference
from app.security.access import (
    AccessContext,
    AccessGrant,
    AuthenticationRequiredError,
    InvalidAccessTokenError,
    PasswordLoginResponse,
    access_profile_from_context,
)
import app.main as main_module
from app.security.http import get_access_context

E2E_AUTH_SUBJECT = UUID('00000000-0000-0000-0000-000000000101')
E2E_PUBLIC_USER = UUID('00000000-0000-0000-0000-000000000201')
E2E_ACCESS_CONTEXT = AccessContext(
    user_id=E2E_PUBLIC_USER,
    auth_subject=E2E_AUTH_SUBJECT,
    role_name='pmo',
    allowed_subportfolio_ids=frozenset(),
    allowed_project_ids=frozenset(),
    can_read=True,
    can_write=False,
    can_export=True,
    grants=(
        AccessGrant(
            permission_scope='portfolio',
            subportfolio_id=None,
            project_id=None,
            can_read=True,
            can_write=False,
            can_export=True,
        ),
    ),
    display_name='Usuario E2E',
    email='usuario.e2e@oneshot.example.com',
)


def authenticate_e2e_persona(profile_key, password):
    if profile_key != 'pmo' or password != 'e2e-password':
        raise InvalidAccessTokenError()
    return PasswordLoginResponse(
        access_token='e2e-token',
        profile=access_profile_from_context(E2E_ACCESS_CONTEXT),
    )


def resolve_e2e_access(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AccessContext:
    if authorization is None:
        raise AuthenticationRequiredError()
    if authorization != 'Bearer e2e-token':
        raise InvalidAccessTokenError()
    request.state.access_context = E2E_ACCESS_CONTEXT
    request.state.access_correlation_id = str(uuid4())
    return E2E_ACCESS_CONTEXT

def generate(request, intent=None, entities=None, access_context=None):
    if request.message == 'falha':
        raise GeminiAPIError('detalhe privado do provedor', status_code=503)
    # S5-23: falhas de comunicacao produzidas pelo proprio backend.
    if request.message == 'falha-gateway':
        raise GeminiAPIError('corpo bruto do provedor com detalhe privado', status_code=502)
    if request.message == 'falha-inesperada':
        raise RuntimeError('detalhe privado de excecao inesperada')
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
    if 'alerta' in text.casefold():
        return SimpleNamespace(
            macrointencao='TRANSACAO', intencao='alerta_prazo_atraso',
            confianca_macro=.99, confianca_intencao=.97,
            fluxo='Workflow guiado de alerta',
            handler='handler:alerta_prazo_atraso', alternativas=[],
            roteada=True, resposta_sugerida=None,
        )
    if 'relat' in text.casefold():
        return SimpleNamespace(
            macrointencao='TRANSACAO', intencao='transacao_gerar_relatorio',
            confianca_macro=.99, confianca_intencao=.98,
            fluxo='Workflow guiado de relatorio',
            handler='handler:transacao_gerar_relatorio', alternativas=[],
            roteada=True, resposta_sugerida=None,
        )
    return SimpleNamespace(
        macrointencao='CONSULTA', intencao='consulta_status_projeto',
        confianca_macro=.95, confianca_intencao=.9,
        fluxo='Consulta de status', handler='handler:consulta_status_projeto',
        alternativas=[], roteada=True, resposta_sugerida=None,
    )


async def transcribe(data, probe, language):
    return transcription.Transcription(text='pergunta de áudio', confidence=.95,
        duration_seconds=probe.duration_seconds)


pipeline.generate_chat_response = generate
inference.classify = classify
transcription.transcribe = transcribe
main_module.authenticate_persona = authenticate_e2e_persona
app.dependency_overrides[get_access_context] = resolve_e2e_access
