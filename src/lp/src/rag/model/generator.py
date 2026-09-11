"""A geração da resposta, a partir dos trechos recuperados.

O prompt tem uma regra que vale mais que todas as outras: **responder só com o
que está nos trechos**. Um agente de portfólio que inventa um número é pior que
um que diz não saber, porque o gestor não tem como distinguir o inventado do
correto sem reabrir o documento — que é justamente o trabalho que a ferramenta
existe para poupar.

A chamada usa o mesmo endpoint de `interactions` que a bancada em `src/backend`
já exercita com esta chave, inclusive o `previous_interaction_id`, que é o que
faz o encadeamento de turnos sem o backend guardar histórico.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from model.config import ModelSettings
from model.store import SearchHit

GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

INSTRUCAO = (
    "Você é o assistente do OneShot e responde perguntas sobre o projeto do "
    "Agente de IA para o Portfólio de Projetos do Metrô de São Paulo, "
    "desenvolvido pelo grupo Oneshot no Inteli.\n\n"
    "Regras:\n"
    "1. Responda apenas com o que estiver nos trechos abaixo. Se eles não "
    "contiverem a resposta, diga claramente que a documentação consultada não "
    "cobre isso — nunca complete com conhecimento próprio nem suponha números.\n"
    "2. Cite as fontes no formato [Fonte N] logo após a afirmação que vem "
    "delas.\n"
    "3. Escreva em português do Brasil, de forma direta. Duas ou três frases "
    "bastam, a menos que a pergunta peça detalhe.\n"
    "4. Se a pergunta for ambígua, responda o que der e diga o que ficou em "
    "aberto."
)


class GenerationError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class GenerationResult:
    text: str
    model: str
    interaction_id: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)


def build_prompt(question: str, hits: list[SearchHit]) -> str:
    """Monta o texto enviado ao modelo."""

    if not hits:
        return (
            f"{INSTRUCAO}\n\n"
            "Nenhum trecho da documentação foi recuperado para esta pergunta. "
            "Diga que não encontrou a informação na documentação disponível.\n\n"
            f"Pergunta do usuário: {question}"
        )

    blocos = []
    for numero, hit in enumerate(hits, start=1):
        blocos.append(
            "\n".join(
                (
                    f"[Fonte {numero}] {hit.chunk.document} — {hit.chunk.section}",
                    f"Trecho: {hit.chunk.text}",
                )
            )
        )

    return (
        f"{INSTRUCAO}\n\n"
        f"Trechos recuperados da documentação:\n\n" + "\n\n".join(blocos) + "\n\n"
        f"Pergunta do usuário: {question}"
    )


def _extract_text(body: dict[str, Any]) -> str:
    """Lê o texto da resposta, no mesmo formato que a bancada já trata."""

    partes: list[str] = []
    for passo in body.get("steps", []):
        if passo.get("type") != "model_output":
            continue
        for conteudo in passo.get("content", []):
            texto = conteudo.get("text") if conteudo.get("type") == "text" else None
            if isinstance(texto, str) and texto.strip():
                partes.append(texto.strip())
    return "\n\n".join(partes)


async def generate(
    question: str,
    hits: list[SearchHit],
    settings: ModelSettings,
    previous_interaction_id: str | None = None,
) -> GenerationResult:
    payload: dict[str, Any] = {
        "model": settings.generation_model,
        "input": build_prompt(question, hits),
        "store": True,
        "generation_config": {
            "max_output_tokens": settings.max_output_tokens,
            "thinking_level": settings.thinking_level,
        },
    }
    if previous_interaction_id:
        payload["previous_interaction_id"] = previous_interaction_id

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.require_api_key(),
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            resposta = await client.post(
                GEMINI_INTERACTIONS_URL, json=payload, headers=headers
            )
    except httpx.HTTPError as erro:
        raise GenerationError(f"Falha de rede ao falar com o Gemini: {erro}") from erro

    if resposta.status_code >= 400:
        raise GenerationError(
            f"O Gemini respondeu {resposta.status_code}: {resposta.text[:200]}",
            status_code=502 if resposta.status_code >= 500 else resposta.status_code,
        )

    corpo = resposta.json()
    texto = _extract_text(corpo)
    if not texto:
        raise GenerationError("O Gemini não devolveu texto algum.")

    return GenerationResult(
        text=texto,
        model=str(corpo.get("model") or settings.generation_model),
        interaction_id=corpo.get("id"),
        usage=corpo.get("usage", {}) or {},
    )
