"""Isolamento global da suite contra credenciais externas do ambiente local."""

import pytest


EXTERNAL_SERVICE_ENV_VARS = (
    "DATABASE_URL",
    "SUPABASE_DATABASE_URL",
    "GEMINI_API_KEY",
    "AZURE_SPEECH_RESOURCE",
    "AZURE_SPEECH_ENDPOINT",
    "AZURE_SPEECH_KEY",
    "AUDIO_SIMULATED_IDENTITIES",
)


@pytest.fixture(autouse=True)
def isolate_external_service_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exige opt-in explicito para qualquer integracao externa em cada teste."""

    for variable in EXTERNAL_SERVICE_ENV_VARS:
        monkeypatch.delenv(variable, raising=False)
