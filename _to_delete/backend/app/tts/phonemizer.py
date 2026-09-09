VOWELS = set("aeiouáéíóúâêôãõà")

DIGRAPHS = {
    "ch": "CH",
    "lh": "LH",
    "nh": "NH",
    "rr": "RR",
    "ss": "SS",
    "qu": "K",
    "gu": "G",
}


def phonemize(text: str) -> list[str]:
    words = text.split()
    phonemes: list[str] = []

    for word_index, word in enumerate(words):
        phonemes.extend(_phonemize_word(word))

        if word_index < len(words) - 1:
            phonemes.append(" ")

    return phonemes


def _phonemize_word(word: str) -> list[str]:
    phonemes: list[str] = []
    index = 0

    while index < len(word):
        pair = word[index : index + 2]

        if pair in DIGRAPHS:
            phonemes.append(DIGRAPHS[pair])
            index += 2
            continue

        char = word[index]

        if char == "ç":
            phonemes.append("S")
        elif char == "x":
            phonemes.append("X")
        elif char == "h":
            pass
        elif char in VOWELS:
            phonemes.append(_normalize_vowel(char))
        elif char.isalpha():
            phonemes.append(char.upper())

        index += 1

    return phonemes


def _normalize_vowel(char: str) -> str:
    return {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "an",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "on",
        "ú": "u",
    }.get(char, char)
