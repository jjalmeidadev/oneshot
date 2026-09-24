"""Métricas estatísticas usadas nas avaliações do recuperador."""

from __future__ import annotations

import math


def wilson_interval(
    successes: int,
    total: int,
    *,
    z_score: float = 1.959963984540054,
) -> tuple[float, float]:
    """Calcula o intervalo de Wilson bilateral para uma proporção binomial."""

    if total <= 0:
        raise ValueError("total deve ser positivo")
    if successes < 0 or successes > total:
        raise ValueError("successes deve estar entre zero e total")

    proportion = successes / total
    denominator = 1 + (z_score**2 / total)
    center = proportion + (z_score**2 / (2 * total))
    margin = z_score * math.sqrt(
        (proportion * (1 - proportion) / total)
        + (z_score**2 / (4 * total**2))
    )
    return (
        max(0.0, (center - margin) / denominator),
        min(1.0, (center + margin) / denominator),
    )
