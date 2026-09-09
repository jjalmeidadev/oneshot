"""Montagem do serviço.

Sobe três objetos de processo e os deixa em `app.state`:

* `store` — a sala em memória (`app/live/store.py`);
* `hub`   — os WebSockets abertos (`app/live/hub.py`);
* `model` — a ponte com o modelo RAG (`app/model/client.py`).

O hub é inscrito no store, de modo que toda escrita na sala vira um envio para
os observadores sem que nenhuma rota precise se lembrar disso.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import BACKEND_DIR, get_settings
from app.live.hub import LiveHub
from app.live.store import LiveStore
from app.model.client import RagModelError, build_model
from app.model.client import NotConfiguredModel
from app.routers import chat, documents, health, live

load_dotenv(Path(BACKEND_DIR) / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")


async def _sweeper(app: FastAPI) -> None:
    """Tira da sala quem parou de dar sinal de vida."""

    settings = get_settings()
    while True:
        await asyncio.sleep(settings.sweep_interval_seconds)
        try:
            expired = await app.state.store.sweep()
            if expired:
                logger.info("Sessões expiradas removidas: %s", ", ".join(expired))
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Falha na faxina de sessões.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.store = LiveStore(settings)
    app.state.hub = LiveHub()
    # Toda mudança na sala vira um envio para os observadores.
    app.state.store.subscribe(app.state.hub.broadcast)

    try:
        app.state.model = build_model(settings)
    except RagModelError as error:
        # Configuração incompleta não deve impedir o serviço de subir: o painel
        # ao vivo continua funcionando e só o chat responde 503.
        logger.warning("Modelo RAG indisponível: %s", error)
        app.state.model = NotConfiguredModel()

    logger.info("Modelo RAG: %s", app.state.model.name)

    sweeper = asyncio.create_task(_sweeper(app))
    try:
        yield
    finally:
        sweeper.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await sweeper


app = FastAPI(
    title="Backend ao vivo — OneShot",
    description=(
        "Presença ao vivo das conversas com o agente do Metrô e ponte para o "
        "modelo RAG. Estrutura inicial: o modelo ainda não está implementado."
    ),
    version=__version__,
    lifespan=lifespan,
)

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.allowed_origins,
    # Não há cookie nem sessão autenticada; liberar credenciais junto com "*"
    # nem seria aceito pelo navegador.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(live.router)
app.include_router(chat.router)
app.include_router(documents.router)
