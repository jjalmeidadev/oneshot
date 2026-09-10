"""O pacote `model` é importado pelo nome, então a pasta `rag/` entra no path."""

from __future__ import annotations

import sys
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parents[2]
if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))
