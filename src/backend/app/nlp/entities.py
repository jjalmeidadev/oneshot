"""Extracao de entidades do dominio do portfolio.

Etapa seguinte ao pre-processamento no pipeline de PLN: enquanto o
classificador decide **o que** foi pedido (a intencao), a extracao identifica
**sobre o que** o pedido fala — projeto, subportfolio, periodo, responsavel,
documento, criterio, indicador, status, risco, frequencia, canal e data. A
Secao 3.4.2 de `docs/Projeto.md` situa a extracao entre o classificador e a
busca, e a entidade `EntidadeExtraida` aparece na Secao 3.1.2.

A extracao trabalha sobre o **texto cru**, nao sobre os tokens. O tokenizador
da `config_22` quebra em `[^\\W_]+`, o que separaria "PRJ-2031" em "PRJ" e
"2031" e destruiria justamente a forma que identifica o projeto.

Duas fontes se combinam:

* **Lexico** — vocabulario conhecido do portfolio, em `data/lexico_dominio.json`.
  O casamento ignora caixa e acento, porque o canal recebe texto digitado: as
  variacoes do conjunto sintetico incluem maiusculas e remocao de acento.
* **Padroes** — expressoes regulares para valores que nao cabem em lista
  fechada: codigo de projeto, percentual, prazo em dias e data. Elas
  generalizam para valores que o lexico nao conhece.

Quando dois termos se sobrepoem, vence o mais longo: em "extensao da Linha
5-Lilas" a entidade e o projeto inteiro, nao a linha isolada.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

LEXICON_PATH = Path(__file__).resolve().parent / "data" / "lexico_dominio.json"

# Alguns termos pertencem a mais de um tipo: "aderencia ao cronograma" e ao
# mesmo tempo criterio de comparacao e indicador de desempenho, e qual dos dois
# vale depende da intencao da solicitacao — "compare por aderencia" usa o termo
# como criterio, "qual a aderencia" o usa como indicador. O extrator nao tem
# essa informacao, entao registra todos os tipos possiveis em `tipos` e deixa a
# escolha para quem ja conhece a intencao. `tipo` guarda o mais provavel, pela
# precedencia abaixo, para o consumidor que nao quer tratar a ambiguidade.
TYPE_PRECEDENCE = ("projeto", "subportfolio", "indicador", "criterio")


@dataclass(frozen=True)
class Entidade:
    """Trecho do texto identificado como um elemento do dominio."""

    tipo: str
    valor: str
    texto: str
    inicio: int
    fim: int
    tipos: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.tipos:
            object.__setattr__(self, "tipos", (self.tipo,))

    @property
    def ambigua(self) -> bool:
        """Verdadeiro quando o termo pertence a mais de um tipo do dominio."""

        return len(self.tipos) > 1


def extract_entities(text: str) -> list[Entidade]:
    """Devolve as entidades do texto, sem sobreposicao e em ordem de leitura."""

    if not text:
        return []

    normalized = _normalize(text)
    candidates = [
        *_lexicon_matches(normalized, text),
        *_pattern_matches(normalized, text),
    ]
    return _resolve_overlaps(candidates)


def _normalize(text: str) -> str:
    """Minusculas e sem acento, preservando o comprimento do texto.

    Preservar o comprimento e o que permite casar sobre o texto normalizado e
    devolver as posicoes do texto original.
    """

    return "".join(
        unicodedata.normalize("NFD", char)[0].lower() for char in text
    )


@lru_cache(maxsize=1)
def _lexicon() -> dict[str, list[tuple[str, str]]]:
    """Mapeia o termo normalizado para os pares (tipo, valor canonico)."""

    data = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    index: dict[str, list[tuple[str, str]]] = {}
    for tipo, definition in data["tipos"].items():
        for termo in definition["termos"]:
            index.setdefault(_normalize(termo), []).append((tipo, termo))
    return index


@lru_cache(maxsize=1)
def _lexicon_pattern() -> re.Pattern[str]:
    """Alternancia unica com os termos do lexico, do mais longo ao mais curto."""

    termos = sorted(_lexicon(), key=len, reverse=True)
    return re.compile(
        r"(?<!\w)(?:" + "|".join(re.escape(termo) for termo in termos) + r")(?!\w)"
    )


# Valores fora de lista fechada. O codigo de projeto exige ao menos tres letras
# para nao capturar siglas curtas coladas a numero.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("projeto", re.compile(r"(?<!\w)[a-z]{3,}-\d{3,}(?!\w)")),
    ("percentual", re.compile(r"(?<!\w)\d{1,3}(?:[.,]\d+)?\s*%")),
    ("data", re.compile(r"(?<!\w)\d{2}/\d{2}/\d{4}(?!\w)")),
    ("prazo_dias", re.compile(r"(?<!\w)\d{1,4}\s+dias?(?!\w)")),
)


def _lexicon_matches(normalized: str, original: str) -> list[Entidade]:
    lexicon = _lexicon()
    entities: list[Entidade] = []
    for match in _lexicon_pattern().finditer(normalized):
        options = lexicon[match.group()]
        tipo, valor = _preferred_type(options)
        entities.append(
            Entidade(
                tipo=tipo,
                valor=valor,
                texto=original[match.start() : match.end()],
                inicio=match.start(),
                fim=match.end(),
                tipos=tuple(_sorted_types(options)),
            )
        )
    return entities


def _pattern_matches(normalized: str, original: str) -> list[Entidade]:
    entities: list[Entidade] = []
    for tipo, pattern in PATTERNS:
        for match in pattern.finditer(normalized):
            texto = original[match.start() : match.end()]
            entities.append(
                Entidade(
                    tipo=tipo,
                    valor=texto.strip(),
                    texto=texto,
                    inicio=match.start(),
                    fim=match.end(),
                )
            )
    return entities


def _rank(tipo: str) -> tuple[int, str]:
    position = (
        TYPE_PRECEDENCE.index(tipo)
        if tipo in TYPE_PRECEDENCE
        else len(TYPE_PRECEDENCE)
    )
    return position, tipo


def _preferred_type(options: list[tuple[str, str]]) -> tuple[str, str]:
    if len(options) == 1:
        return options[0]
    return min(options, key=lambda option: _rank(option[0]))


def _sorted_types(options: list[tuple[str, str]]) -> list[str]:
    return sorted({tipo for tipo, _ in options}, key=_rank)


def _resolve_overlaps(candidates: list[Entidade]) -> list[Entidade]:
    """Mantem o trecho mais longo em cada regiao do texto.

    Empate de comprimento e resolvido pela posicao e depois pela precedencia de
    tipo, para que a saida seja estavel entre execucoes.
    """

    def sort_key(entity: Entidade) -> tuple[int, int, int]:
        position = (
            TYPE_PRECEDENCE.index(entity.tipo)
            if entity.tipo in TYPE_PRECEDENCE
            else len(TYPE_PRECEDENCE)
        )
        return -(entity.fim - entity.inicio), entity.inicio, position

    selected: list[Entidade] = []
    for entity in sorted(candidates, key=sort_key):
        if any(
            entity.inicio < chosen.fim and chosen.inicio < entity.fim
            for chosen in selected
        ):
            continue
        selected.append(entity)

    return sorted(selected, key=lambda entity: entity.inicio)
