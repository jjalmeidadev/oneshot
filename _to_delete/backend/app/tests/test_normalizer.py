from app.tts.normalizer import normalize_text


def test_normalize_text_expands_project_code_and_percentage() -> None:
    text = "O projeto TAP-01 está 75% concluído."

    assert (
        normalize_text(text)
        == "o projeto tap zero um está setenta e cinco por cento concluído"
    )


def test_normalize_text_collapses_symbols_and_spaces() -> None:
    text = "Status: avanço + riscos / cronograma"

    assert normalize_text(text) == "status avanço mais riscos cronograma"
