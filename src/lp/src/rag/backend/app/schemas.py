"""Contratos de entrada e saída do serviço.

Este arquivo é a fronteira com o frontend: os campos de `LiveSession` e
`LiveMessage` reproduzem exatamente as interfaces declaradas em
`lp/src/lib/useLivePresence.ts`, inclusive o `lastSeen` em camelCase e os
carimbos de tempo em **milissegundos** (o mesmo que `Date.now()` devolve no
navegador, que é o que o cartão de presença usa para calcular "há 12s").
Mudar um nome aqui quebra a LP silenciosamente — mude nos dois lados.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

#: Autor de uma mensagem, na mesma nomenclatura do frontend.
Role = Literal["user", "assistant"]
#: Estado exibido ao lado do nome no painel de presença.
SessionStatus = Literal["typing", "thinking", "idle"]


class LiveMessage(BaseModel):
    """Uma fala da conversa observada."""

    id: str
    role: Role
    content: str
    #: Epoch em milissegundos.
    at: int


class LiveSession(BaseModel):
    """Um visitante conversando com o agente agora."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    #: Cor do participante, no espírito dos cursores do Miro.
    color: str
    status: SessionStatus = "idle"
    #: Epoch em milissegundos do último sinal de vida. Serializado como
    #: `lastSeen` porque é assim que o frontend lê.
    last_seen: int = Field(alias="lastSeen")
    messages: list[LiveMessage] = Field(default_factory=list)


class LiveSessionsResponse(BaseModel):
    """Corpo de `GET /api/live/sessions` — o que o polling da LP consome."""

    sessions: list[LiveSession] = Field(default_factory=list)


class JoinRequest(BaseModel):
    """Entrada de um visitante na sala."""

    #: Opcional: sem nome, o servidor gera um "Convidado N".
    name: str | None = Field(default=None, max_length=60)


class HeartbeatRequest(BaseModel):
    """Sinal de vida da sessão, opcionalmente atualizando o estado exibido."""

    status: SessionStatus | None = None


# --- Chat ----------------------------------------------------------------


class ChatRequest(BaseModel):
    """Pergunta de um visitante ao agente."""

    #: Sessão que fez a pergunta, obtida em `POST /api/live/sessions`. É o que
    #: liga a pergunta ao painel ao vivo; sem ela a interação não é observável.
    session_id: str | None = Field(default=None, max_length=64)
    message: str = Field(..., min_length=1, max_length=20000)
    #: Encadeamento de turnos, no mesmo espírito do backend de bancada.
    previous_interaction_id: str | None = Field(default=None, max_length=1024)


class ChatSource(BaseModel):
    """Documento que sustenta uma resposta.

    `document` é o rótulo que a pasta de fontes da LP exibe (ver
    `components/chat/source-folder.tsx`) e `download_url` é o caminho servido
    por `app/routers/documents.py`, para que a fonte seja de fato baixável.
    """

    id: str
    title: str
    document: str
    download_url: str | None = None
    #: Trecho recuperado, quando o modelo devolver — a LP ainda não exibe.
    excerpt: str | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    """Resposta do agente, com a procedência junto."""

    text: str
    model: str
    interaction_id: str | None = None
    latency_ms: int = 0
    sources: list[ChatSource] = Field(default_factory=list)


# --- Documentos ----------------------------------------------------------


class DocumentInfo(BaseModel):
    """Um arquivo disponível em `lp/src/rag/documentsRAG`."""

    id: str
    name: str
    size_bytes: int
    download_url: str


class DocumentsResponse(BaseModel):
    documents: list[DocumentInfo] = Field(default_factory=list)


# --- WebSocket -----------------------------------------------------------


class LiveEvent(BaseModel):
    """Mensagem empurrada pelo `/ws/live`.

    Um único formato para os dois casos (`snapshot` na conexão e `sessions` a
    cada mudança): o cliente sempre recebe a sala inteira e substitui o que
    tinha. Com a sala limitada a algumas dezenas de sessões, o payload é
    pequeno o suficiente para não valer a complexidade de um diff.
    """

    type: Literal["snapshot", "sessions"] = "sessions"
    sessions: list[LiveSession] = Field(default_factory=list)
