"""A bancada de teste da sala.

Uma página só, servida pelo próprio backend, para exercitar a sala com vários
dispositivos ao mesmo tempo: cada aparelho abre este endereço, entra na sala,
manda mensagem e vê os outros aparecerem ao vivo. Como ela vem da mesma origem
da API, não há endereço para configurar no celular — só abrir a URL.

Não faz parte do produto. Ela existe porque o chat da landing page ainda é
roteirizado, então sem isto não haveria como um dispositivo entrar na sala de
verdade. Desligue com `ENABLE_TEST_BENCH=false` fora do desenvolvimento.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from app.config import BACKEND_DIR, get_settings

BENCH_FILE = BACKEND_DIR / "app" / "static" / "bancada.html"

router = APIRouter(tags=["bancada"])


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Quem abrir só o endereço do servidor cai onde é útil."""

    destino = "/teste" if get_settings().enable_test_bench else "/docs"
    return RedirectResponse(destino)


@router.get("/teste", include_in_schema=False)
def bench() -> FileResponse:
    if not get_settings().enable_test_bench:
        raise HTTPException(status_code=404, detail="Bancada desligada.")
    return FileResponse(BENCH_FILE, media_type="text/html")
