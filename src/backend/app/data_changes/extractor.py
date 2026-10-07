"""Extrator deterministico de pedidos de alteracao (S5-05, Secao 8.5.13).

Nenhum modelo de linguagem participa do caminho da escrita: o pedido e lido
por regras sobre o texto, e o que faltar vira pergunta. O extrator so
reconhece o pedido e separa as partes. Permissao, existencia do registro e
validade do valor ficam com o servico.

Uma mensagem e tratada como pedido de alteracao quando traz um verbo de
alteracao e um termo de campo (ou um status, no caso de "marca o marco X como
concluido"). Perguntas ("qual o prazo...") nunca sao interceptadas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from app.data_changes.fields import (
    MONTH_MENTION_PATTERN,
    NUMBER_PATTERN,
    find_dates,
    find_month_only,
    find_status,
    fold,
)

PROJECT_CODE_PATTERN = re.compile(r"\bPRJ-[A-Z0-9]+(?:-[A-Z0-9]+)*\b", re.IGNORECASE)

_VERB = re.compile(
    r"\b(?:"
    r"alter(?:ar|a|e|em|ando)|mud(?:ar|a|e|em|ando)|atualiz(?:ar|a|e|em|ando)|"
    r"prorrog(?:ar|a|ue|uem|ando)|adi(?:ar|a|e|em|ando)|antecip(?:ar|a|e|em|ando)|"
    r"marc(?:ar|a|ue|uem|ando)|defin(?:ir|e|a|am|indo)|pass(?:ar|a|e|em|ando)|"
    r"troc(?:ar|a|ue|uem|ando)|coloc(?:ar|a|que|quem|ando)|reprogram(?:ar|a|e|em|ando)|"
    r"ajust(?:ar|a|e|em|ando)|registr(?:ar|a|e|em|ando)|mov(?:er|e|a|endo)"
    r")\b"
)
_STATUS_VERBS = re.compile(r"\b(?:marc|coloc|pass)\w*\b")
_QUESTION_START = re.compile(
    r"^\s*(?:e\s+)?(?:qual|quais|quando|quem|quant[oa]s?|onde|por\s*que|o\s+que|como|"
    r"sera\s+que|existe|existem|ha\b|houve)"
)

_ENTITY_KEYWORDS = (
    ("cronograma", re.compile(r"\b(?:atividades?|tarefas?)\b")),
    ("marco", re.compile(r"\b(?:marcos?|entregas?|entregaveis?)\b")),
    ("risco", re.compile(r"\b(?:riscos?|problemas?)\b")),
)

_FIELD_TERMS = {
    "conclusion": re.compile(r"\b(?:data\s+de\s+conclusao|conclusao|concluid[oa]\s+em)\b"),
    "date": re.compile(r"\b(?:prazos?|datas?|termino|fim|vencimento|previsao)\b"),
    "status": re.compile(r"\b(?:status|situacao|estado)\b"),
    "progress": re.compile(r"\b(?:progresso|avanco|percentual)\b|%|\bpor\s+cento\b"),
    "owner": re.compile(r"\b(?:responsavel|dono)\b"),
}
_NOT_EDITABLE = re.compile(
    r"\b(?:orcamento|custos?|escopo|titulo|nome|descricao|gerente|patrocinador|sponsor|"
    r"criticidade|probabilidade|impacto|prioridade|severidade|fase|inicio|beneficios?)\b"
)

#: Campo do contrato para cada tipo de termo, por registro.
_FIELD_BY_KIND = {
    "projeto": {"date": "projeto.prazo_final", "status": "projeto.status"},
    "cronograma": {
        "date": "cronograma.prazo",
        "status": "cronograma.status",
        "progress": "cronograma.progresso",
    },
    "marco": {
        "conclusion": "marco.data_conclusao",
        "date": "marco.data_prevista",
        "status": "marco.status",
    },
    "risco": {"status": "risco.status", "owner": "risco.responsavel", "date": "risco.prazo"},
}

#: Mascaras de mesmo comprimento: o codigo do projeto vira "#" e a data, "§".
CODE_MASK = "#"
DATE_MASK = "§"
_MASKS = {CODE_MASK, DATE_MASK}

_REFERENCE_END = re.compile(
    r"\s+(?:d[oa]s?|n[oa]s?|em)\s+(?:projeto\s+)?#"
    r"|\s+(?:para|pra|como|ate)\b"
    r"|\s+(?:em|no\s+dia|na\s+data\s+de|ate|para|pra)?\s*§"
    r"|[?!;]|\.(?:\s|$)|$"
)
_VALUE_MARKER = re.compile(r"\b(?:para|pra|como)\b")


@dataclass(frozen=True)
class ExtractedChange:
    """Partes reconhecidas no pedido. Campos ausentes viram pergunta."""

    entity: str
    field: str | None
    project_code: str | None
    item_reference: str | None
    raw_value: str | None
    #: Codigo de recusa ja identificavel no texto (MULTIPLE_CHANGES etc.).
    problem: str | None = None
    #: Mes informado sem dia ("ate marco"): o chat pergunta pelo dia.
    missing_day: bool = False


def extract_change(message: str, today: date) -> ExtractedChange | None:
    """Reconhece um pedido de alteracao ou devolve `None` para seguir o fluxo normal."""

    folded = fold(message)
    if _QUESTION_START.match(folded) or not _VERB.search(folded):
        return None

    codes = sorted({code.upper() for code in PROJECT_CODE_PATTERN.findall(message)})
    masked = _mask(
        folded, [match.span() for match in PROJECT_CODE_PATTERN.finditer(message)], CODE_MASK
    )
    dates = [(start, end, value) for start, end, value in find_dates(message, today)
             if not _inside_code(start, end, message)]
    masked = _mask(masked, [(start, end) for start, end, _ in dates], DATE_MASK)
    month_only = find_month_only(masked)
    if month_only:
        masked = _mask(masked, [month_only.span()], DATE_MASK)
    # Datas por extenso que nao sao validas tambem saem da deteccao.
    malformed_dates = [match.span() for match in MONTH_MENTION_PATTERN.finditer(masked)]
    malformed_dates += [match.span() for match in re.finditer(r"(?<![\w-])\d+(?:[/-]\d+)+", masked)]
    masked = _mask(masked, malformed_dates, DATE_MASK)

    entity, keyword_end = _entity(masked)
    reference_span = None
    reference = None
    if entity != "projeto":
        reference_span = _reference_span(message, masked, keyword_end)
        if reference_span:
            reference = message[reference_span[0]:reference_span[1]].strip(" \"'“”:,-")
            reference = reference or None

    scope = _mask(masked, [reference_span]) if reference_span else masked
    kinds = {kind for kind, pattern in _FIELD_TERMS.items() if pattern.search(scope)}
    if "conclusion" in kinds:
        kinds.discard("date")
        if entity != "marco":
            kinds.discard("conclusion")
            kinds.add("date")
    not_editable = bool(_NOT_EDITABLE.search(scope))

    value_start = _value_start(scope)
    value_text = message[value_start:] if value_start is not None else None
    status_value = find_status(value_text) if value_text else None

    if not kinds and not not_editable:
        # "marca o marco X como concluido": o status vem pelo valor.
        if status_value and (entity != "projeto" or _STATUS_VERBS.search(folded)):
            kinds = {"status"}
        else:
            return None

    problem = None
    if len(codes) > 1:
        problem = "MULTIPLE_CHANGES"
    elif not_editable:
        problem = "FIELD_NOT_EDITABLE"
    elif len(kinds) > 1:
        problem = "MULTIPLE_CHANGES"

    field = None
    if problem is None:
        kind = next(iter(kinds))
        field = _FIELD_BY_KIND[entity].get(kind)
        if field is None:
            problem = "FIELD_NOT_EDITABLE"

    raw_value = None
    missing_day = False
    if field:
        if field.endswith(("prazo", "prazo_final", "data_prevista", "data_conclusao")):
            usable = [(start, end) for start, end, _value in dates
                      if not reference_span or not (reference_span[0] <= start < reference_span[1])]
            if usable:
                start, end = usable[-1]
                raw_value = message[start:end]
            elif month_only:
                missing_day = True
            else:
                # Algo com cara de data que nao e data valida ("31/03/20277")
                # segue para a validacao e e recusado, em vez de virar pergunta.
                spans = [span for span in malformed_dates
                         if not reference_span or not (reference_span[0] <= span[0] < reference_span[1])]
                raw_value = message[spans[-1][0]:spans[-1][1]] if spans else None
        elif field.endswith("status"):
            raw_value = status_value or find_status(_strip(message, scope))
            if raw_value is None and value_text:
                raw_value = value_text.strip() or None
        elif field.endswith("progresso"):
            # O numero vai inteiro para a validacao: com sinal, todas as casas
            # e o separador original (#260, revisao do MR).
            numbers = NUMBER_PATTERN.findall(value_text or _strip(message, scope))
            raw_value = numbers[-1].replace("−", "-") if numbers else None
        elif field.endswith("responsavel"):
            if value_text:
                raw_value = value_text.strip().rstrip(".!") or None

    return ExtractedChange(
        entity=entity,
        field=field,
        project_code=codes[0] if len(codes) == 1 else None,
        item_reference=reference,
        raw_value=raw_value,
        problem=problem,
        missing_day=missing_day,
    )


def _mask(text: str, spans: list[tuple[int, int]], mask: str = " ") -> str:
    characters = list(text)
    for start, end in spans:
        for index in range(start, min(end, len(characters))):
            characters[index] = mask
    return "".join(characters)


def _inside_code(start: int, end: int, message: str) -> bool:
    return any(code_start <= start and end <= code_end
               for code_start, code_end in (m.span() for m in PROJECT_CODE_PATTERN.finditer(message)))


def _entity(masked: str) -> tuple[str, int]:
    best: tuple[int, str, int] | None = None
    for entity, pattern in _ENTITY_KEYWORDS:
        match = pattern.search(masked)
        if match and (best is None or match.start() < best[0]):
            best = (match.start(), entity, match.end())
    if best is None:
        return "projeto", 0
    return best[1], best[2]


def _reference_span(message: str, masked: str, start: int) -> tuple[int, int] | None:
    rest = masked[start:]
    quoted = re.match(r"\s*(?:de\s+|d[oa]\s+)?[\"“']([^\"”']+)[\"”']", message[start:])
    if quoted:
        return start + quoted.start(1), start + quoted.end(1)
    leading = re.match(r"\s*(?::|chamad[oa]|intitulad[oa]|de\s+nome)?\s*", rest)
    begin = start + (leading.end() if leading else 0)
    # Comeca um caractere antes para que "do PRJ-..." logo apos a palavra
    # "risco" tambem conte como fim (sem nome de registro).
    end_match = _REFERENCE_END.search(masked, max(begin - 1, start))
    end = max(end_match.start(), begin) if end_match else len(masked)
    if end <= begin or not masked[begin:end].strip():
        return None
    return begin, end


def _value_start(scope: str) -> int | None:
    last = None
    for match in _VALUE_MARKER.finditer(scope):
        last = match
    return last.end() if last else None


def _strip(message: str, scope: str) -> str:
    """Texto original com os trechos mascarados apagados."""

    return "".join(" " if mask in _MASKS or (mask == " " and original != " ") else original
                   for original, mask in zip(message, scope))
