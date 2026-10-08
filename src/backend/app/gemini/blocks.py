"""Blocos de apresentacao derivados exclusivamente de afirmacoes verificadas."""

import re
from typing import Annotated, Literal, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from app.gemini.schemas import FactualClaim


class ReferencedBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    citation_ids: list[str] = Field(min_length=1)


class TableRow(ReferencedBlock):
    cells: list[str] = Field(min_length=1)


class TableBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["table"] = "table"
    columns: list[str] = Field(min_length=1)
    rows: list[TableRow] = Field(min_length=1)

    @model_validator(mode="after")
    def rectangular(self):
        if any(len(row.cells) != len(self.columns) for row in self.rows):
            raise ValueError("Cada linha deve ter uma celula por coluna")
        return self


class IndicatorBlock(ReferencedBlock):
    type: Literal["indicator"] = "indicator"
    label: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False, strict=True)
    unit: Literal["%"] | None = None


class HighlightBlock(ReferencedBlock):
    type: Literal["highlight"] = "highlight"
    text: str = Field(min_length=1)


ResponseBlock = Annotated[
    TableBlock | IndicatorBlock | HighlightBlock, Field(discriminator="type")
]

# Numeros isolados em atributos: nunca extrair numeros de datas, IDs ou prosa.
# Aceita decimal brasileiro ou ponto; separadores de milhar ambiguos sao omitidos.
_NUMBER = re.compile(r"([+-]?\d{1,15}(?:[,.]\d{1,2})?)\s*(%)?")


def build_blocks(claims: list["FactualClaim"]) -> list[ResponseBlock]:
    blocks = []
    rows = []
    for claim in claims:
        blocks.append(HighlightBlock(text=claim.text, citation_ids=claim.citation_ids))
        evidence = claim.evidence[0] if claim.evidence else None
        if evidence and evidence.field == "attribute" and evidence.attribute:
            label = evidence.attribute
            value = evidence.quote[len(label) + 2:]
            rows.append(TableRow(cells=[label, value], citation_ids=claim.citation_ids))
            number = _NUMBER.fullmatch(value.strip())
            if number:
                blocks.append(IndicatorBlock(
                    label=label, value=float(number[1].replace(",", ".")),
                    unit=number[2], citation_ids=claim.citation_ids,
                ))
        else:
            rows.append(TableRow(cells=["Informação", claim.text], citation_ids=claim.citation_ids))
    if len(rows) > 1:
        blocks.insert(0, TableBlock(columns=["Informação", "Valor"], rows=rows))
    return blocks
