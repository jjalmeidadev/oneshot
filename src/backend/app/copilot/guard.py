"""Protecoes minimas antes de despachar uma entrada para automacao ou LLM."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import unquote

from app.copilot.errors import UnsafeDispatchInputError

_BIDI_CONTROLS = frozenset(
    {
        "\u202a",
        "\u202b",
        "\u202c",
        "\u202d",
        "\u202e",
        "\u2066",
        "\u2067",
        "\u2068",
        "\u2069",
    }
)
_UNSAFE_PATTERNS = (
    re.compile(
        r"\b(?:ignore|disregard|bypass)\b.{0,40}\b(?:instruction|policy|system)\w*",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:ignore|desconsidere|contorne)\b.{0,40}\b(?:instruc|politica|sistema)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:system prompt|prompt do sistema|developer message)\b", re.IGNORECASE
    ),
    re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)"),
    re.compile(r"(?:<script\b|javascript:|\$\([^\r\n)]*\))", re.IGNORECASE),
)


def ensure_safe_dispatch_input(value: str) -> None:
    """Rejeita sinais objetivos de override, ofuscacao e injecao de codigo."""

    if any(character in _BIDI_CONTROLS for character in value):
        raise UnsafeDispatchInputError()

    compatible = unicodedata.normalize("NFKC", unquote(value)).casefold()
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", compatible)
        if not unicodedata.combining(character)
    )
    if any(pattern.search(normalized) for pattern in _UNSAFE_PATTERNS):
        raise UnsafeDispatchInputError()
