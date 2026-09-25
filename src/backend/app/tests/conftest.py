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
    "SUPABASE_SERVICE_ROLE_KEY",
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
