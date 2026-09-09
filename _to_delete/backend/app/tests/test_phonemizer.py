from app.tts.phonemizer import phonemize


def test_phonemize_detects_common_portuguese_digraphs() -> None:
    assert phonemize("chave linha amanhã carro passo") == [
        "CH",
        "a",
        "V",
        "e",
        " ",
        "L",
        "i",
        "NH",
        "a",
        " ",
        "a",
        "M",
        "a",
        "NH",
        "an",
        " ",
        "C",
        "a",
        "RR",
        "o",
        " ",
        "P",
        "a",
        "SS",
        "o",
    ]
