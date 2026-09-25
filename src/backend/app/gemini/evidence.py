"""Validacao extrativa: o modelo seleciona evidencias, nunca inventa fatos."""

import re
import unicodedata
from typing import Literal, NamedTuple

from app.gemini.schemas import ClaimEvidence, FactualClaim, GeminiSource

INSUFFICIENT_EVIDENCE = "Não há evidência recuperada suficiente para responder com rastreabilidade."
RECOMMENDATION_PREFIX = "Sugestão:"

# Aceita [Fonte 1], (Fonte 1), [Fonte 1, Fonte 2] e [Fontes 1 e 2]; a resposta
# final e sempre reescrita no formato canonico [Fonte N].
_CITATION_GROUP = r"[\[(]Fontes? [1-9]\d*(?:\s*(?:,|e)\s*(?:Fonte )?[1-9]\d*)*[\])]"
_CITATION = re.compile(_CITATION_GROUP)
_TERMINAL_CITATIONS = re.compile(rf"(?:{_CITATION_GROUP}\s*)+[.!]?$")
_CITATION_NUMBER = re.compile(r"[1-9]\d*")
_LIST_MARKER = re.compile(r"^(?:[-*•]|\d+[.)])\s+")
_EMPHASIS = re.compile(r"\*\*|`")
_RECOMMENDATION = re.compile(r"^sugestao\s*:\s*", re.IGNORECASE)


class ValidatedAnswer(NamedTuple):
    text: str
    claims: list[FactualClaim]
    status: Literal["referenced", "insufficient"]
    recommendation: str | None = None


def normalize_quote(text: str) -> str:
    """So espacos de apresentacao; preserva numeros, negacoes, caixa e acentos."""
    return re.sub(r"\s+", " ", text).strip()


def comparable_quote(text: str) -> str:
    """Chave de comparacao: ignora acentos e o ponto final, nunca palavras ou numeros.

    A massa sintetica e escrita sem acentos e o modelo tende a acentua-la ao
    copiar; o ponto antes da citacao tambem costuma ser omitido. Nenhuma das
    duas diferencas altera o conteudo copiado.
    """
    decomposed = unicodedata.normalize("NFKD", normalize_quote(text))
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return plain.rstrip(".!;").rstrip()


def source_units(source: GeminiSource) -> list[ClaimEvidence]:
    """Unidades completas: nunca aceita substring que possa omitir condicoes."""
    if not source.citation_id:
        return []
    units = []
    if source.excerpt and source.excerpt.strip():
        units.append(ClaimEvidence(citation_id=source.citation_id,
            field="excerpt", quote=source.excerpt))
    for key, value in source.attributes.items():
        if value.strip():
            units.append(ClaimEvidence(citation_id=source.citation_id,
                field="attribute", attribute=key, quote=f"{key}: {value}"))
    return units


def render_answer(claims: list[FactualClaim], recommendation: str | None = None) -> str:
    """Texto publico montado somente a partir do que foi verificado."""
    lines = [f"{claim.text} " + " ".join(f"[{citation_id}]" for citation_id in claim.citation_ids)
             for claim in claims]
    if recommendation:
        lines.append(f"{RECOMMENDATION_PREFIX} {recommendation}")
    return "\n".join(lines)


def recommendation_problem(recommendation: str) -> str | None:
    """Sugestao e analise, nao fato: uma linha, sem numeros, datas ou citacoes."""
    if not recommendation.strip() or "\n" in recommendation:
        return "Sugestao deve ocupar uma unica linha"
    if any(char.isdigit() for char in recommendation):
        return "Sugestao nao pode introduzir numeros ou datas"
    if _CITATION.search(recommendation):
        return "Citacoes ficam nas evidencias, nao na sugestao"
    return None


def _split_citations(line: str) -> tuple[str, list[str]] | None:
    """Separa o texto das citacoes finais; None quando ha citacao no meio."""
    suffix = _TERMINAL_CITATIONS.search(line)
    body = line[:suffix.start()].strip() if suffix else line
    if _CITATION.search(body):
        return None
    ids = list(dict.fromkeys(
        f"Fonte {number}"
        for group in _CITATION.findall(suffix.group() if suffix else "")
        for number in _CITATION_NUMBER.findall(group)))
    return body, ids


def validate_evidence(
    text: str,
    sources: list[GeminiSource],
    *,
    allow_recommendation: bool = False,
) -> ValidatedAnswer:
    """Aceita apenas copias integrais de unidades das fontes citadas.

    Nao usa outro modelo para julgar o primeiro. Uma citacao existente so e
    aceita quando o texto e igual ao trecho completo ou atributo identificado,
    desconsiderando acentos, ponto final, marcador de lista e negrito.
    Parafrases, recortes de frases, numeros alterados e mistura de fontes
    resultam em abstencao. Cabecalhos sem citacao (linha terminada em ":")
    sao descartados, pois o texto publico e remontado so com o que foi
    verificado. Esta garantia e de fidelidade a origem, nao de veracidade ou
    atualidade da propria origem.

    Com `allow_recommendation`, usado apenas na resposta secundaria da
    proatividade, uma unica linha iniciada por "Sugestão:" e aceita como
    recomendacao rotulada, desde que acompanhe ao menos uma evidencia
    verificada e nao introduza numeros, datas ou citacoes.
    """
    units = {source.citation_id: source_units(source) for source in sources}
    claims = []
    recommendation = None
    for raw_line in text.splitlines():
        line = _EMPHASIS.sub("", raw_line).strip()
        if not line:
            continue
        parsed = _split_citations(line)
        if parsed is None:
            return _insufficient()
        claim_text, ids = parsed
        unmarked = _LIST_MARKER.sub("", claim_text)
        if allow_recommendation and _RECOMMENDATION.match(comparable_quote(unmarked)):
            # A sugestao pode apontar as fontes da analise, mas elas precisam existir.
            if recommendation is not None or not set(ids) <= set(units):
                return _insufficient()
            recommendation = normalize_quote(unmarked.split(":", 1)[1])
            if recommendation_problem(recommendation):
                return _insufficient()
            continue
        if not ids:
            if claim_text.startswith("#") or claim_text.endswith(":"):
                continue
            return _insufficient()
        if not claim_text:
            return _insufficient()
        candidates = {comparable_quote(claim_text), comparable_quote(unmarked)}
        evidence = []
        for citation_id in ids:
            matched = next((unit for unit in units.get(citation_id, [])
                if comparable_quote(unit.quote) in candidates), None)
            if matched is None:
                return _insufficient()
            evidence.append(matched)
        canonical = normalize_quote(evidence[0].quote)
        claims.append(FactualClaim(text=canonical, citation_ids=ids, evidence=evidence))
    if not claims:
        return _insufficient()
    return ValidatedAnswer(render_answer(claims, recommendation), claims, "referenced", recommendation)


def _insufficient() -> ValidatedAnswer:
    return ValidatedAnswer(INSUFFICIENT_EVIDENCE, [], "insufficient")
