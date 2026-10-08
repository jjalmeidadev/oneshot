"""Limites de domínio aplicados depois da previsão, sem recalibrar o modelo.

As probabilidades continuam sendo as do modelo. Uma regra de roteamento não
é uma nova probabilidade nem uma alteração dos atributos usados no benchmark.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import replace
from typing import TYPE_CHECKING

from app.nlp.entities import extract_entities

if TYPE_CHECKING:
    from app.nlp.inference import Classificacao


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


# Temas presentes em base_atendimento.json e procedimentos_operacionais.json.
# fullmatch limita a exceção a consultas; citar um tema em uma transação não
# autoriza essa transação nem converte pedidos mistos em consulta.
_TOPIC_QUERY = re.compile(
    r"(?:(?:fale|me fale|explique|me explique|conte|me conte) (?:sobre )?(?:o |os |a |as )?"
    r"|(?:quero|preciso de) (?:informacoes|saber) sobre (?:o |os |a |as )?"
    r"|como (?:funciona|funcionam) (?:o |os |a |as )?"
    r"|o que (?:e|sao) (?:o |os |a |as )?)?"
    r"(?:bilhete digital|objetos perdidos|achados e perdidos)[?.!]*"
)
_STATUS_QUERY = re.compile(
    r"(?:mostre|me mostre|exiba|informe|consulte|qual(?: e)?) "
    r"(?:(?:o|a) )?(?:status|andamento|situacao) (?:do|da|de) (?P<scope>.+?)[?.!]*"
)
_RESERVATION = re.compile(r"\b(?:reserve|reservar|reserva|alugue|alugar)\b.*\bsala\b")
_SCHEDULING = re.compile(
    r"\b(?:agende|agendar|marque|marcar|reserve|reservar)\b.*"
    r"\b(?:reuniao|compromisso|checkpoint|revisao|sala)\b"
)
_NEGATION = re.compile(r"\b(?:nao|nunca|nem|sem)\b")

SCHEDULING_LIMITATION = (
    "Não realizo reservas de salas nem agendamentos sem vínculo com o "
    "portfólio. Você pode consultar um tema, como 'Bilhete digital', ou "
    "pedir uma reunião de acompanhamento de um projeto ou portfólio."
)
SCHEDULING_LIMITATION_HANDLER = "limitacao:agendamento"


def apply_domain_routes(result: Classificacao) -> Classificacao:
    """Reconhece consultas explícitas e bloqueia agendamento fora do domínio."""
    from app.nlp.inference import LIMITATION_FLOW, _fluxo_da_macro

    text = _normalize(result.texto)
    has_scope = any(
        entity.tipo in {"projeto", "subportfolio"}
        for entity in extract_entities(result.texto)
    ) or bool(re.search(r"\b(?:projeto|programa|portfolio|subportfolio)\b|\blinha\s+\d+\b", text))

    if _RESERVATION.search(text) or (
        not has_scope
        and (
            result.intencao == "transacao_agendar_compromisso"
            or (_SCHEDULING.search(text) and not _NEGATION.search(text))
        )
    ):
        return replace(
            result, macrointencao="FORA_DE_ESCOPO", intencao=None,
            fluxo=LIMITATION_FLOW, handler=SCHEDULING_LIMITATION_HANDLER,
            resposta_sugerida=SCHEDULING_LIMITATION,
            regra_roteamento="limite_agendamento",
        )

    if _TOPIC_QUERY.fullmatch(text):
        return replace(
            result, macrointencao="CONSULTA", intencao=None,
            fluxo=_fluxo_da_macro("CONSULTA"),
            handler="fluxo genérico de CONSULTA", resposta_sugerida=None,
            regra_roteamento="consulta_tema_operacional",
        )

    status_match = _STATUS_QUERY.fullmatch(text)
    if status_match and has_scope and not _NEGATION.search(text):
        # Uma solicitação mista não pode virar uma consulta de status simples.
        if not re.search(r"\b(?:e|depois|tambem|atualize|altere|mude|registre|agende)\b", status_match["scope"]):
            return replace(
                result, macrointencao="CONSULTA", intencao="consulta_status_projeto",
                fluxo=_fluxo_da_macro("CONSULTA"),
                handler="handler:consulta_status_projeto", resposta_sugerida=None,
                regra_roteamento="consulta_status_explicita",
            )

    return result
