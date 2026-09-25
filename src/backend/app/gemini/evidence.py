"""Validacao extrativa: o modelo seleciona evidencias, nunca inventa fatos."""

import re
from typing import Literal

from app.gemini.schemas import ClaimEvidence, FactualClaim, GeminiSource

INSUFFICIENT_EVIDENCE = "Nao ha evidencia recuperada suficiente para responder com rastreabilidade."
_CITATION = re.compile(r"\[Fonte ([1-9]\d*)\]")
_TERMINAL_CITATIONS = re.compile(r"(?:\[Fonte [1-9]\d*\]\s*)+[.!]?$")


def normalize_quote(text: str) -> str:
    """So espacos de apresentacao; preserva numeros, negacoes, caixa e acentos."""
    return re.sub(r"\s+", " ", text).strip()


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


def validate_evidence(
    text: str, sources: list[GeminiSource],
) -> tuple[str, list[FactualClaim], Literal["referenced", "insufficient"]]:
    """Aceita apenas copias integrais de unidades das fontes citadas.

    Nao usa outro modelo para julgar o primeiro. Uma citacao existente so e
    aceita quando o texto e igual ao trecho completo ou atributo identificado.
    Parafrases, recortes de frases, numeros alterados e mistura de fontes
    resultam em abstencao. Esta garantia e de fidelidade a origem, nao de
    veracidade ou atualidade da propria origem.
    """
    units = {source.citation_id: source_units(source) for source in sources}
    claims = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        suffix = _TERMINAL_CITATIONS.search(line)
        if not suffix:
            return INSUFFICIENT_EVIDENCE, [], "insufficient"
        claim_text = line[:suffix.start()].strip()
        claim_text = re.sub(r"^[-*] +", "", claim_text)
        if _CITATION.search(claim_text) or not claim_text:
            return INSUFFICIENT_EVIDENCE, [], "insufficient"
        ids = list(dict.fromkeys(f"Fonte {match.group(1)}"
            for match in _CITATION.finditer(suffix.group())))
        evidence = []
        for citation_id in ids:
            matched = next((unit for unit in units.get(citation_id, [])
                if normalize_quote(unit.quote) == normalize_quote(claim_text)), None)
            # Aceita ponto final colocado depois da citacao pelo modelo.
            if matched is None and suffix.group().endswith("."):
                matched = next((unit for unit in units.get(citation_id, [])
                    if normalize_quote(unit.quote) == normalize_quote(claim_text + ".")), None)
            if matched is None:
                return INSUFFICIENT_EVIDENCE, [], "insufficient"
            evidence.append(matched)
        canonical = normalize_quote(evidence[0].quote)
        claims.append(FactualClaim(text=canonical, citation_ids=ids, evidence=evidence))
    if not claims:
        return INSUFFICIENT_EVIDENCE, [], "insufficient"
    answer = "\n".join(f"{claim.text} " + " ".join(
        f"[{citation_id}]" for citation_id in claim.citation_ids) for claim in claims)
    return answer, claims, "referenced"
