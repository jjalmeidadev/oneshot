"""Atalho para subir o serviço: `python run.py`.

Equivale a `uvicorn app.main:app --reload`. Existe para não depender de o
`uvicorn` estar no PATH — em ambiente virtual no Windows isso costuma variar.
"""

from __future__ import annotations

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
