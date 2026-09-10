"""Configuração do serviço, lida do ambiente.

Um único lugar para os valores ajustáveis, de modo que nenhum número mágico
fique espalhado pelas rotas. Todos têm padrão utilizável: o serviço sobe sem
nenhuma variável de ambiente definida.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# `app/config.py` -> `app/` -> raiz do backend (`lp/src/rag/backend`).
BACKEND_DIR = Path(__file__).resolve().parents[1]
# Pasta irmã onde ficarão os documentos vetorizados e oferecidos para download.
DEFAULT_DOCUMENTS_DIR = BACKEND_DIR.parent / "documentsRAG"


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "sim", "on"}


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Parâmetros de execução do serviço."""

    # --- Rede -------------------------------------------------------------
    #: Origens autorizadas no CORS. A LP roda em outra porta durante o
    #: desenvolvimento, então o padrão libera geral — decisão consciente para
    #: esta etapa, em que ainda não há dado real nem autenticação. Em produção,
    #: preencha com o domínio da landing page.
    allowed_origins: list[str] = field(default_factory=lambda: ["*"])
    #: Origens aceitas por expressão regular, além da lista acima. Existe por
    #: causa dos preview deploys da Vercel, cujo domínio muda a cada branch:
    #: `https://.*\\.vercel\\.app` cobre todos de uma vez.
    allowed_origin_regex: str = ""

    # --- Presença ao vivo -------------------------------------------------
    #: Segundos sem sinal de vida até a sessão sair da sala. Precisa ser
    #: folgado o bastante para sobreviver a uma aba em segundo plano.
    session_ttl_seconds: int = 90
    #: De quanto em quanto tempo a faxina de sessões expiradas roda.
    sweep_interval_seconds: int = 15
    #: Teto de sessões simultâneas, para a sala não crescer sem limite.
    max_sessions: int = 50
    #: Quantas mensagens ficam guardadas por sessão (as mais antigas caem).
    max_messages_per_session: int = 200

    # --- Modelo RAG -------------------------------------------------------
    #: `local` roda o modelo de `lp/src/rag/model` dentro deste processo — é o
    #: que o projeto usa. `http` fala com o modelo publicado como serviço
    #: próprio. `none` (padrão) recusa com 503. Ver `app/model/client.py`.
    model_backend: str = "none"
    #: URL do modelo quando `model_backend` é `http`.
    model_url: str = ""
    #: Tempo máximo de espera por uma resposta do modelo.
    model_timeout_seconds: int = 60

    # --- Documentos -------------------------------------------------------
    #: Pasta servida pelas rotas de download das fontes.
    documents_dir: Path = DEFAULT_DOCUMENTS_DIR

    # --- Bancada de teste -------------------------------------------------
    #: Serve a página `/teste`, usada para exercitar a sala com vários
    #: dispositivos. É uma bancada, não produto: desligue fora do
    #: desenvolvimento, já que ela entra na sala sem autenticação nenhuma.
    enable_test_bench: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Configuração do processo, montada uma única vez a partir do ambiente."""

    documents_raw = os.getenv("DOCUMENTS_DIR", "").strip()
    return Settings(
        allowed_origins=_env_list("CORS_ALLOW_ORIGINS", ["*"]),
        allowed_origin_regex=os.getenv("CORS_ALLOW_ORIGIN_REGEX", "").strip(),
        session_ttl_seconds=_env_int("SESSION_TTL_SECONDS", 90),
        sweep_interval_seconds=_env_int("SWEEP_INTERVAL_SECONDS", 15),
        max_sessions=_env_int("MAX_SESSIONS", 50),
        max_messages_per_session=_env_int("MAX_MESSAGES_PER_SESSION", 200),
        model_backend=os.getenv("RAG_MODEL_BACKEND", "none").strip().lower() or "none",
        model_url=os.getenv("RAG_MODEL_URL", "").strip(),
        model_timeout_seconds=_env_int("RAG_MODEL_TIMEOUT_SECONDS", 60),
        documents_dir=Path(documents_raw) if documents_raw else DEFAULT_DOCUMENTS_DIR,
        enable_test_bench=_env_bool("ENABLE_TEST_BENCH", True),
    )
