import pytest

from app.rag.evaluation import wilson_interval


def test_wilson_interval_for_perfect_recall_is_not_overconfident() -> None:
    lower, upper = wilson_interval(72, 72)

    assert lower == pytest.approx(0.9493, abs=0.0001)
    assert upper == 1.0


def test_wilson_interval_rejects_invalid_counts() -> None:
    with pytest.raises(ValueError):
        wilson_interval(1, 0)

    with pytest.raises(ValueError):
        wilson_interval(3, 2)
