"""Acesso aos objetos de processo (sala, hub e modelo).

Eles vivem em `app.state`, montados no `lifespan` de `app/main.py`. Passar por
`Depends` em vez de importar variáveis globais é o que permite trocá-los nos
testes com `app.dependency_overrides`.
"""

from __future__ import annotations

from starlette.requests import HTTPConnection

from app.live.hub import LiveHub
from app.live.store import LiveStore
from app.model.client import RagModel


def get_store(connection: HTTPConnection) -> LiveStore:
    return connection.app.state.store


def get_hub(connection: HTTPConnection) -> LiveHub:
    return connection.app.state.hub


def get_model(connection: HTTPConnection) -> RagModel:
    return connection.app.state.model
