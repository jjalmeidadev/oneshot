"""Identidade corporativa e limite de concorrencia do endpoint de audio.

A autenticacao da solucao **nao e feita por este backend**. Conforme a Secao
6.2.4 de docs/Projeto.md, a identidade vem do **Microsoft Entra ID**: o agente
vive dentro do Teams, e o canal entrega quem e a pessoa junto com a mensagem.
Cabe a API apenas validar o token recebido e extrair o identificador do
usuario — nunca tratar senha, login ou cadastro.

Na prova de conceito o ambiente corporativo nao esta provisionado, entao o
token do Entra e substituido por um token simulado, declarado em
`AUDIO_SIMULATED_IDENTITIES` no formato `<token>=<entra_object_id>`. O formato
do identificador devolvido e o mesmo que a coluna `users.entra_object_id`
espera, de modo que a consulta real a `access_rules` — necessaria para o
`403 OUT_OF_SCOPE_FOR_PROFILE` — se conecte aqui sem reescrever a rota.

A autorizacao de dominio (qual subportfolio ou projeto cada perfil alcanca)
continua sendo responsabilidade da solucao: o Entra informa quem e a pessoa,
nao o que ela pode ver do portfolio. Esse e o risco R04 da Secao 3.6.

O limite de uma requisicao simultanea por usuario vem da Secao 8.7.3 e existe
para evitar consumo concorrente da franquia gratuita do provedor de STT.

Quando a rota textual tambem passar a exigir identidade, este modulo deve
subir para `app/security.py`: nada aqui e especifico de audio.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from hashlib import sha256
from threading import Lock

from app.audio.errors import RateLimitedError, UnauthenticatedError

SIMULATED_IDENTITIES_ENV = "AUDIO_SIMULATED_IDENTITIES"

_active_identities: set[str] = set()
_active_identities_lock = Lock()


@dataclass(frozen=True)
class CorporateIdentity:
    """Usuario autenticado pelo Entra ID, como o canal o entrega a API."""

    object_id: str


def resolve_identity(authorization: str | None) -> CorporateIdentity:
    """Valida o token recebido do canal e devolve a identidade do usuario.

    Em producao o token e o emitido pelo Entra ID e o `object_id` sai da
    propria credencial. Na prova de conceito ele vem do mapa simulado; quando
    o mapa nao esta configurado, o identificador e derivado do token de forma
    estavel, para que o controle de concorrencia e a futura consulta de
    permissoes tenham uma chave consistente. O token em si nunca e guardado.
    """

    scheme, _, token = (authorization or "").partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise UnauthenticatedError()

    identities = _simulated_identities()
    if identities:
        if token not in identities:
            raise UnauthenticatedError()
        return CorporateIdentity(object_id=identities[token])

    return CorporateIdentity(object_id=_derived_object_id(token))


def _simulated_identities() -> dict[str, str]:
    """Le o mapa `<token>=<entra_object_id>` da variavel de ambiente.

    Entrada sem `=` e aceita como token sem identidade declarada, caso em que
    o identificador tambem e derivado do token.
    """

    raw = os.getenv(SIMULATED_IDENTITIES_ENV, "")
    identities: dict[str, str] = {}
    for item in raw.split(","):
        entry = item.strip()
        if not entry:
            continue
        token, separator, object_id = entry.partition("=")
        token = token.strip()
        object_id = object_id.strip()
        if not token:
            continue
        identities[token] = object_id if separator and object_id else _derived_object_id(token)
    return identities


def _derived_object_id(token: str) -> str:
    """Identificador estavel para o token, sem guardar o token em memoria."""

    return sha256(token.encode("utf-8")).hexdigest()


class single_request_per_identity:
    """Reserva a vaga de processamento do usuario enquanto o audio e tratado."""

    def __init__(self, identity: CorporateIdentity) -> None:
        self._object_id = identity.object_id

    def __enter__(self) -> "single_request_per_identity":
        with _active_identities_lock:
            if self._object_id in _active_identities:
                raise RateLimitedError()
            _active_identities.add(self._object_id)
        return self

    def __exit__(self, *_args: object) -> None:
        with _active_identities_lock:
            _active_identities.discard(self._object_id)
