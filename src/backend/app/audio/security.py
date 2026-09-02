"""Autenticacao e limite de concorrencia do endpoint de audio.

A autenticacao corporativa do RNF02 e simulada na prova de conceito, conforme
a Secao 3.2.4 de docs/Projeto.md. O cabecalho `Authorization: Bearer <TOKEN>`
e sempre obrigatorio; quando `AUDIO_API_TOKENS` esta definida no ambiente,
apenas os tokens listados sao aceitos.

O limite de uma requisicao simultanea por usuario vem da Secao 8.7.3 e existe
para evitar consumo concorrente da franquia gratuita do provedor de STT.
"""

from __future__ import annotations

import os
from hashlib import sha256
from threading import Lock

from app.audio.errors import RateLimitedError, UnauthenticatedError

_active_users: set[str] = set()
_active_users_lock = Lock()


def authenticate(authorization: str | None) -> str:
    """Valida o token e devolve a chave que identifica o usuario.

    O token nunca e guardado em memoria: o controle de concorrencia usa apenas
    o seu resumo.
    """

    scheme, _, token = (authorization or "").partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise UnauthenticatedError()

    allowed = [
        item.strip()
        for item in os.getenv("AUDIO_API_TOKENS", "").split(",")
        if item.strip()
    ]
    if allowed and token not in allowed:
        raise UnauthenticatedError()

    return sha256(token.encode("utf-8")).hexdigest()


class single_request_per_user:
    """Reserva a vaga de processamento do usuario enquanto o audio e tratado."""

    def __init__(self, user_key: str) -> None:
        self._user_key = user_key

    def __enter__(self) -> "single_request_per_user":
        with _active_users_lock:
            if self._user_key in _active_users:
                raise RateLimitedError()
            _active_users.add(self._user_key)
        return self

    def __exit__(self, *_args: object) -> None:
        with _active_users_lock:
            _active_users.discard(self._user_key)
