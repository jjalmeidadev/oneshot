"""Fronteira com o modelo RAG.

O modelo ainda não existe: ele será construído em `lp/src/rag/model` quando os
documentos a vetorizar estiverem completos. Para que o backend possa ser
escrito, testado e demonstrado antes disso, o modelo entra aqui como uma
dependência trocável.

Duas implementações acompanham o pacote:

* `NotConfiguredModel` — o padrão. Recusa a chamada com uma mensagem explícita,
  e a rota de chat a traduz em `503`. Nada é inventado: o serviço prefere dizer
  que o modelo não está pronto a devolver uma resposta falsa.
* `HttpRagModel` — fala com o modelo publicado como serviço HTTP próprio, seja
  ele escrito em Python ou em TypeScript. Serve para separar o modelo em outro
  serviço quando fizer sentido; basta apontar `RAG_MODEL_URL`.
* `LocalRagModel` (`app/model/local.py`) — **o que o projeto usa**. Importa o
  pipeline de `lp/src/rag/model` e roda no mesmo processo: um deploy só, sem
  rede entre backend e modelo.

A escolha é feita por `RAG_MODEL_BACKEND` e resolvida em `build_model`.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.config import Settings
from app.schemas import ChatSource


class RagModelError(RuntimeError):
    """Falha ao consultar o modelo."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class RagModelNotConfigured(RagModelError):
    """O modelo ainda não foi ligado a este serviço."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=503)


class ModelAnswer:
    """Resposta do modelo, já no vocabulário do serviço."""

    def __init__(
        self,
        text: str,
        model: str = "desconhecido",
        interaction_id: str | None = None,
        sources: list[ChatSource] | None = None,
    ) -> None:
        self.text = text
        self.model = model
        self.interaction_id = interaction_id
        self.sources = sources or []


class RagModel(Protocol):
    """O que o backend precisa que o modelo saiba fazer."""

    name: str

    async def answer(
        self,
        question: str,
        previous_interaction_id: str | None = None,
    ) -> ModelAnswer: ...


class NotConfiguredModel:
    """Implementação padrão enquanto `lp/src/rag/model` não existir."""

    name = "não configurado"

    async def answer(
        self,
        question: str,
        previous_interaction_id: str | None = None,
    ) -> ModelAnswer:
        raise RagModelNotConfigured(
            "O modelo RAG ainda não está configurado. Defina RAG_MODEL_BACKEND=http "
            "e RAG_MODEL_URL apontando para o serviço de lp/src/rag/model."
        )


class HttpRagModel:
    """Modelo publicado como serviço HTTP.

    Espera um `POST` com `{"question": ..., "previous_interaction_id": ...}` e
    uma resposta `{"text": ..., "model": ..., "interaction_id": ...,
    "sources": [...]}`. As fontes seguem o formato de `ChatSource`; campos
    ausentes são tolerados para que uma primeira versão do modelo já funcione
    devolvendo apenas `text`.
    """

    name = "http"

    def __init__(
        self,
        url: str,
        timeout_seconds: int = 60,
        transport: Any = None,
    ) -> None:
        self._url = url
        self._timeout = timeout_seconds
        # Só os testes preenchem `transport`, para exercitar este caminho sem
        # subir um servidor de mentira.
        self._transport = transport

    async def answer(
        self,
        question: str,
        previous_interaction_id: str | None = None,
    ) -> ModelAnswer:
        # Importado aqui para que o pacote continue utilizável sem httpx
        # instalado enquanto o modelo não é usado.
        import httpx

        payload = {
            "question": question,
            "previous_interaction_id": previous_interaction_id,
        }
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, transport=self._transport
            ) as client:
                response = await client.post(self._url, json=payload)
        except Exception as error:  # noqa: BLE001
            raise RagModelError(f"Não foi possível falar com o modelo RAG: {error}") from error

        if response.status_code >= 400:
            raise RagModelError(
                f"O modelo RAG respondeu {response.status_code}.",
                status_code=502,
            )

        try:
            body: dict[str, Any] = response.json()
        except ValueError as error:
            raise RagModelError("O modelo RAG devolveu um corpo que não é JSON.") from error

        return ModelAnswer(
            text=str(body.get("text", "")),
            model=str(body.get("model", "rag")),
            interaction_id=body.get("interaction_id"),
            sources=[ChatSource(**source) for source in body.get("sources", [])],
        )


def build_model(settings: Settings) -> RagModel:
    """Escolhe a implementação do modelo a partir da configuração."""

    if settings.model_backend == "local":
        # Importado aqui para o backend continuar subindo mesmo sem as
        # dependências do modelo instaladas.
        from app.model.local import build_local_model  # noqa: PLC0415

        return build_local_model(settings)

    if settings.model_backend == "http":
        if not settings.model_url:
            raise RagModelNotConfigured(
                "RAG_MODEL_BACKEND=http exige RAG_MODEL_URL preenchido."
            )
        return HttpRagModel(settings.model_url, settings.model_timeout_seconds)
    return NotConfiguredModel()
