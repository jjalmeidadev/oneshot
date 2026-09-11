"""Ambiente comum dos testes.

O ambiente é preparado antes de `app.main` ser importado: a pasta de
documentos aponta para um diretório temporário e o TTL é curto, para que o
teste de expiração não precise esperar um minuto e meio.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session", autouse=True)
def environment(tmp_path_factory) -> Path:
    documents = tmp_path_factory.mktemp("documentsRAG")
    os.environ["DOCUMENTS_DIR"] = str(documents)
    os.environ["SESSION_TTL_SECONDS"] = "1"
    os.environ["SWEEP_INTERVAL_SECONDS"] = "1"
    os.environ["MAX_MESSAGES_PER_SESSION"] = "4"
    os.environ["RAG_MODEL_BACKEND"] = "none"

    from app.config import get_settings

    get_settings.cache_clear()
    return documents


@pytest.fixture
def documents_dir(environment: Path) -> Path:
    for leftover in environment.iterdir():
        leftover.unlink()
    return environment


@pytest.fixture
def client(environment):
    # O `with` executa o lifespan, então cada teste recebe uma sala vazia.
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
