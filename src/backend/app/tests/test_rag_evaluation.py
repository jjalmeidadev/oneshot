import json
from collections import Counter
from pathlib import Path

import pytest

from app.rag.evaluation import wilson_interval


DATA_DIR = Path(__file__).resolve().parent / "data"


def test_wilson_interval_for_perfect_recall_is_not_overconfident() -> None:
    lower, upper = wilson_interval(72, 72)

    assert lower == pytest.approx(0.9493, abs=0.0001)
    assert upper == 1.0


def test_wilson_interval_rejects_invalid_counts() -> None:
    with pytest.raises(ValueError):
        wilson_interval(1, 0)

    with pytest.raises(ValueError):
        wilson_interval(3, 2)


def test_prospective_holdout_is_unique_and_balanced() -> None:
    previous = json.loads(
        (DATA_DIR / "rnf06_retrieval_cases.json").read_text(encoding="utf-8")
    )
    holdout = json.loads(
        (DATA_DIR / "rnf06_retrieval_holdout_v2.json").read_text(encoding="utf-8")
    )
    cases = holdout["casos"]
    queries = [case["consulta"] for case in cases]
    ids = [case["id"] for case in cases]
    previous_queries = {case["consulta"] for case in previous["casos"]}

    assert len(cases) == 72
    assert len(set(ids)) == len(ids)
    assert len(set(queries)) == len(queries)
    assert previous_queries.isdisjoint(queries)
    assert set(Counter(case["tipo_variacao"] for case in cases).values()) == {9}
    assert set(
        Counter(case["fontes_esperadas"][0] for case in cases).values()
    ) == {8}
