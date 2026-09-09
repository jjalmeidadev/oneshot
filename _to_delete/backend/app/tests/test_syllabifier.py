from app.tts.syllabifier import syllabify_text, syllabify_word


def test_syllabify_word_uses_basic_portuguese_clusters() -> None:
    assert syllabify_word("projeto") == ["pro", "je", "to"]
    assert syllabify_word("concluido") == ["con", "clui", "do"]
    assert syllabify_word("esta") == ["es", "ta"]


def test_syllabify_text_preserves_word_boundaries() -> None:
    assert syllabify_text("o projeto tap") == ["o", " ", "pro", "je", "to", " ", "tap"]
