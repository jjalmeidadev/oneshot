"""O modelo RAG rodando dentro deste mesmo processo.

É a terceira implementação prevista em `client.py`, e a que o projeto usa: o
pipeline de `lp/src/rag/model` é importado direto, sem serviço intermediário
nem rede entre os dois. Um deploy em vez de dois, e uma origem de falha a
menos na hora da apresentação.

O pacote do modelo é irmão desta pasta (`rag/model` ao lado de `rag/backend`),
então a pasta `rag/` entra no path de importação. É a única concessão à falta
de empacotamento entre os dois — feita num lugar só, e substituível por um
`pip install -e` quando o projeto tiver empacotamento de verdade.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.config import Settings
from app.model.client import ModelAnswer, RagModelError, RagModelNotConfigured
from app.schemas import ChatSource

logger = logging.getLogger(__name__)

#: `app/model/local.py` -> `app/model` -> `app` -> `backend` -> `rag`
RAG_DIR = Path(__file__).resolve().parents[3]


def _import_pipeline():
    """Importa o pacote do modelo, colocando `rag/` no path se preciso."""

    if str(RAG_DIR) not in sys.path:
        sys.path.insert(0, str(RAG_DIR))
    try:
        from model.pipeline import RagPipeline  # noqa: PLC0415
    except ImportError as erro:  # pragma: no cover - depende do disco
        raise RagModelNotConfigured(
            f"Não consegui importar o pacote do modelo em {RAG_DIR / 'model'}: {erro}. "
            "Instale as dependências com `pip install -r ../model/requirements.txt`."
        ) from erro
    return RagPipeline


class LocalRagModel:
    """Adaptador entre o pipeline do modelo e o vocabulário do backend."""

    name = "local"

    def __init__(self) -> None:
        # O índice é carregado na primeira pergunta, não na subida: um índice
        # ausente não deve impedir o serviço (e o painel ao vivo) de existir.
        self._pipeline = None

    def _ensure(self):
        if self._pipeline is None:
            RagPipeline = _import_pipeline()
            self._pipeline = RagPipeline()
        return self._pipeline

    async def answer(
        self,
        question: str,
        previous_interaction_id: str | None = None,
    ) -> ModelAnswer:
        pipeline = self._ensure()

        try:
            resposta = await pipeline.answer(question, previous_interaction_id)
        except FileNotFoundError as erro:
            raise RagModelNotConfigured(
                f"A documentação não foi encontrada: {erro}"
            ) from erro
        except Exception as erro:  # noqa: BLE001
            # O pipeline sinaliza índice ausente e falhas do Gemini com tipos
            # próprios; aqui elas viram o erro que a rota sabe traduzir.
            status = getattr(erro, "status_code", None)
            if type(erro).__name__ == "IndexNotBuilt":
                raise RagModelNotConfigured(str(erro)) from erro
            raise RagModelError(str(erro), status_code=status or 502) from erro

        logger.info(
            "RAG: %d fontes | recuperação %dms | geração %dms",
            len(resposta.sources),
            resposta.retrieval_ms,
            resposta.generation_ms,
        )

        return ModelAnswer(
            text=resposta.text,
            model=resposta.model,
            interaction_id=resposta.interaction_id,
            sources=[
                ChatSource(
                    id=fonte.id,
                    title=fonte.title,
                    document=fonte.document,
                    excerpt=fonte.excerpt,
                    score=fonte.score,
                )
                for fonte in resposta.sources
            ],
        )


def build_local_model(settings: Settings) -> LocalRagModel:
    return LocalRagModel()
