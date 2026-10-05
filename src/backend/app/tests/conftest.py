"""Isolamento do ambiente para a suite do backend.

`app/main.py` chama `load_dotenv` no import do modulo. Sem este arquivo, a suite
passa a enxergar o `.env` real de quem esta desenvolvendo e muda de
comportamento: 21 testes reprovam na maquina de quem tem o backend configurado
e passam na de quem nao tem.

Era o caso antes desta fixture. `AUDIO_SIMULATED_IDENTITIES` preenchida fazia
`resolve_identity` recusar qualquer token fora do mapa, e testes que enviavam um
token arbitrario recebiam 401 no lugar do 400 ou 413 que verificavam.
`GEMINI_API_KEY` presente tirava o caminho de erro de configuracao do ar, e
`SUPABASE_DATABASE_URL` presente levava o RAG ao banco quando o teste esperava o
fallback local.

A inversao e proposital: o ambiente padrao da suite e **vazio**, e cada teste
declara com `monkeypatch.setenv` exatamente o que precisa. Isso mantem o mesmo
resultado na maquina de qualquer integrante e na CI, e impede que um teste passe
por causa de uma credencial que so existe em uma maquina.
"""

import json
import os
from typing import Annotated
from uuid import NAMESPACE_URL, uuid5

from fastapi import Header, Request
import pytest

#: Variaveis que a suite neutraliza antes de cada teste. Todas sao lidas em
#: tempo de requisicao pelo codigo de producao, entao limpar aqui basta: nao e
#: preciso recarregar modulo nem desfazer o `load_dotenv` ja executado.
VARIAVEIS_DE_AMBIENTE_NEUTRALIZADAS = (
    # Provedor do LLM
    "LLM_PROVIDER",
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "GEMINI_MAX_OUTPUT_TOKENS",
    "GEMINI_THINKING_LEVEL",
    "GEMINI_REQUEST_TIMEOUT_SECONDS",
    "GEMINI_MAX_RETRIES",
    "GEMINI_RETRY_BASE_DELAY_SECONDS",
    # Recuperacao
    "DATABASE_POOL_ENABLED",
    "DATABASE_POOL_MAX_SIZE",
    "DATABASE_STATEMENT_TIMEOUT_MS",
    "DATABASE_URL",
    "SUPABASE_DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "MVP_AUTH_PASSWORD",
    "MVP_AUTH_PMO_PASSWORD",
    "MVP_AUTH_SUBPORTFOLIO_LEADER_PASSWORD",
    "MVP_AUTH_PROJECT_MANAGER_PASSWORD",
    "MVP_AUTH_CONSULTA_PASSWORD",
    "RAG_MAX_SOURCES",
    "SHAREPOINT_MOCK_DATA_DIR",
    # Transcricao
    "AZURE_SPEECH_RESOURCE",
    "AZURE_SPEECH_ENDPOINT",
    "AZURE_SPEECH_KEY",
    "AZURE_SPEECH_TIMEOUT_SECONDS",
    "AZURE_SPEECH_MAX_ATTEMPTS",
    "VHS_ENABLED",
    # Identidade simulada do endpoint de audio
    "AUDIO_SIMULATED_IDENTITIES",
    # Proatividade e armazenamento
    "PROACTIVE_SUGGESTION_TTL_SECONDS",
    # As tres variaveis de relatorio ainda nao sao lidas por nenhum modulo desta
    # branch: pertencem a frente de Copilot/Power Automate (#212, #213, #217) e
    # ja circulam no `.env` que a equipe compartilha. Ficam listadas desde agora
    # para que, quando aquele codigo entrar, a suite nao volte a depender do
    # ambiente de quem a executa.
    "REPORT_STORAGE_MODE",
    "REPORT_REPOSITORY_MODE",
    "REPORT_SIMULATED_IDENTITIES",
    "NOTIFICATION_CALLBACK_TOKEN",
    # Aquecimento do classificador: manter desligado deixa a suite rapida e
    # independente do download do BERTimbau.
    "PLN_WARMUP",
)


@pytest.fixture(autouse=True)
def ambiente_isolado(monkeypatch):
    """Zera as variaveis do produto antes de cada teste.

    `raising=False` porque a variavel pode simplesmente nao existir na maquina
    de quem roda a suite — o que e o caso normal na CI.
    """

    from app.audio import transcription
    from app.audio.vhs import ResponseCache
    monkeypatch.setattr(transcription, "response_cache", ResponseCache())
    for nome in VARIAVEIS_DE_AMBIENTE_NEUTRALIZADAS:
        monkeypatch.delenv(nome, raising=False)

    # Sem pool nos testes. Um teste que definisse uma DATABASE_URL ficticia sem
    # injetar `connect` faria o pool tentar conectar em segundo plano e esperar
    # ate o timeout, em vez de falhar na hora como antes. O comportamento do
    # pool tem testes proprios em test_database_pool.py, com pool falso.
    monkeypatch.setenv("DATABASE_POOL_ENABLED", "0")


@pytest.fixture(autouse=True)
def acesso_central_isolado():
    """Evita rede nos testes legados; casos de Auth removem este override."""

    from app.main import app
    from app.security import (
        AccessContext,
        AuthenticationRequiredError,
        InvalidAccessTokenError,
        get_access_context,
    )
    from app.security.access import AccessGrant

    def context_from_payload(payload: dict, token: str) -> AccessContext:
        allow_all = bool(payload.get("allow_all", False))
        projects = frozenset(map(str, payload.get("projects", [])))
        subportfolios = frozenset(map(str, payload.get("subportfolios", [])))
        can_export = bool(payload.get("can_export", True))
        can_write = bool(payload.get("can_write", can_export))
        grants = (
            AccessGrant("portfolio", None, None, True, can_write, can_export),
        ) if allow_all else ()
        subject = uuid5(NAMESPACE_URL, str(payload.get("subject") or token))
        return AccessContext(
            user_id=uuid5(NAMESPACE_URL, f"public:{subject}"),
            auth_subject=payload.get("subject") or subject,
            role_name=str(payload.get("role") or "pmo"),
            allowed_subportfolio_ids=frozenset(),
            allowed_project_ids=frozenset(),
            can_read=bool(payload.get("can_read", True)),
            can_write=can_write,
            can_export=can_export,
            grants=grants,
            allowed_subportfolio_codes=subportfolios,
            allowed_project_codes=projects,
        )

    def legacy_test_access(
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> AccessContext:
        scheme, _, token = (authorization or "").partition(" ")
        token = token.strip()
        if (
            request.url.path.startswith("/api/audio")
            or request.url.path == "/api/chat/proactive-confirmation"
        ) and not token:
            raise AuthenticationRequiredError()

        configured_reports = os.getenv("REPORT_SIMULATED_IDENTITIES", "").strip()
        if configured_reports and token:
            payload = json.loads(configured_reports).get(token)
            if payload is not None:
                return context_from_payload(payload, token)

        configured_audio = os.getenv("AUDIO_SIMULATED_IDENTITIES", "").strip()
        if configured_audio and token:
            tokens = {
                item.partition("=")[0].strip()
                for item in configured_audio.split(",")
                if item.strip()
            }
            if scheme.casefold() != "bearer" or token not in tokens:
                raise InvalidAccessTokenError()

        return context_from_payload(
            {
                "subject": "legacy-test-user",
                "role": "pmo",
                "can_read": True,
                "can_write": True,
                "can_export": True,
                "allow_all": True,
            },
            token or "legacy-test-token",
        )

    app.dependency_overrides[get_access_context] = legacy_test_access
    yield
    app.dependency_overrides.pop(get_access_context, None)


def pytest_configure(config):
    """Registra os marcadores usados pela suite.

    Sem isto, `pytestmark = pytest.mark.integration` gera PytestUnknownMarkWarning
    em cada arquivo marcado. O registro fica aqui, e nao em um `pytest.ini` novo,
    para nao mudar o rootdir da suite.
    """

    config.addinivalue_line(
        "markers",
        "integration: cruza fronteira entre componentes (API, modelo, banco ou "
        "servico externo)",
    )
