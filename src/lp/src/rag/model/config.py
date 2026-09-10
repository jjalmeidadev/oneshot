"""Configuração do modelo, lida do ambiente.

Todos os valores têm padrão utilizável: sem nenhuma variável definida, o
modelo procura a documentação em `docs/` na raiz do repositório e guarda o
índice em `model/artifacts/`. A única coisa realmente obrigatória é a chave da
API — e ela já existe no projeto, em `src/backend/.env`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

# `model/config.py` -> `model/` -> `rag/` -> `lp/src/` -> `lp/` -> `src/` -> raiz.
MODEL_DIR = Path(__file__).resolve().parent
RAG_DIR = MODEL_DIR.parent


def _repo_root() -> Path:
    """Raiz do repositório, quando o pacote está no lugar de sempre.

    Num contêiner o pacote pode estar em `/app/model`, onde não há cinco
    níveis acima — e um IndexError aqui derrubaria a importação inteira. O
    caminho só é usado para achar `docs/` na indexação; servindo respostas,
    ele não é consultado.
    """

    try:
        return MODEL_DIR.parents[4]
    except IndexError:
        return RAG_DIR


REPO_ROOT = _repo_root()

DEFAULT_CORPUS_DIR = REPO_ROOT / "docs"
DEFAULT_DOCUMENTS_DIR = RAG_DIR / "documentsRAG"
DEFAULT_ARTIFACTS_DIR = MODEL_DIR / "artifacts"


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_path(name: str, default: Path) -> Path:
    raw = os.getenv(name, "").strip()
    return Path(raw).expanduser().resolve() if raw else default


class MissingApiKey(RuntimeError):
    """A chave do Gemini não está no ambiente."""


@dataclass(frozen=True)
class ModelSettings:
    """Parâmetros do pipeline."""

    #: Chave do Gemini. A mesma que a bancada em `src/backend` já usa.
    api_key: str = ""

    # --- Embeddings -------------------------------------------------------
    embedding_model: str = "gemini-embedding-2"
    #: 768 é o tamanho recomendado pelo Google e o suficiente para um corpus
    #: desta escala — 3072 triplicaria o índice sem ganho perceptível aqui.
    embedding_dimensions: int = 768
    #: Chamadas simultâneas ao indexar. Acima disso o serviço começa a
    #: devolver 429 e o retry acaba custando mais do que a paralelização rende.
    embedding_concurrency: int = 4

    # --- Geração ----------------------------------------------------------
    generation_model: str = "gemini-3.7-flash"
    max_output_tokens: int = 900
    thinking_level: str = "low"

    # --- Divisão em trechos ----------------------------------------------
    #: Teto de caracteres por trecho. Em português, ~1800 caracteres ficam
    #: perto de 450 tokens — bem abaixo do limite de 8.192 do embedding, e
    #: pequeno o bastante para o trecho recuperado ser específico.
    max_chunk_chars: int = 1800
    #: Sobreposição entre trechos consecutivos, para uma frase cortada no
    #: limite não desaparecer das duas metades.
    chunk_overlap_chars: int = 200

    # --- Recuperação ------------------------------------------------------
    top_k: int = 5
    #: Abaixo disso o trecho é ruído. Serve para o modelo dizer "não encontrei"
    #: em vez de responder com o que estiver menos longe.
    min_score: float = 0.30

    # --- Caminhos ---------------------------------------------------------
    corpus_dir: Path = DEFAULT_CORPUS_DIR
    documents_dir: Path = DEFAULT_DOCUMENTS_DIR
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR

    request_timeout_seconds: int = 60

    def require_api_key(self) -> str:
        if not self.api_key:
            raise MissingApiKey(
                "GEMINI_API_KEY não está definida. Ela já existe em "
                "src/backend/.env — copie para o ambiente do backend da LP."
            )
        return self.api_key


@lru_cache(maxsize=1)
def get_model_settings() -> ModelSettings:
    return ModelSettings(
        api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        embedding_model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2").strip()
        or "gemini-embedding-2",
        embedding_dimensions=_env_int("GEMINI_EMBEDDING_DIMENSIONS", 768),
        embedding_concurrency=_env_int("GEMINI_EMBEDDING_CONCURRENCY", 4),
        generation_model=os.getenv("GEMINI_MODEL", "gemini-3.7-flash").strip()
        or "gemini-3.7-flash",
        max_output_tokens=_env_int("GEMINI_MAX_OUTPUT_TOKENS", 900),
        thinking_level=os.getenv("GEMINI_THINKING_LEVEL", "low").strip() or "low",
        max_chunk_chars=_env_int("RAG_MAX_CHUNK_CHARS", 1800),
        chunk_overlap_chars=_env_int("RAG_CHUNK_OVERLAP_CHARS", 200),
        top_k=_env_int("RAG_TOP_K", 5),
        min_score=_env_float("RAG_MIN_SCORE", 0.30),
        corpus_dir=_env_path("RAG_CORPUS_DIR", DEFAULT_CORPUS_DIR),
        documents_dir=_env_path("RAG_DOCUMENTS_DIR", DEFAULT_DOCUMENTS_DIR),
        artifacts_dir=_env_path("RAG_ARTIFACTS_DIR", DEFAULT_ARTIFACTS_DIR),
        request_timeout_seconds=_env_int("GEMINI_TIMEOUT_SECONDS", 60),
    )
