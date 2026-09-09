def phoneme_duration(phoneme: str) -> float:
    if phoneme == " ":
        return 0.07

    if phoneme in {"a", "e", "i", "o", "u", "an", "on"}:
        return 0.105

    if phoneme in {"CH", "LH", "NH", "RR", "SS", "X"}:
        return 0.075

    return 0.055


def phoneme_frequency(phoneme: str) -> float:
    frequencies = {
        "a": 720.0,
        "e": 660.0,
        "i": 840.0,
        "o": 560.0,
        "u": 480.0,
        "an": 610.0,
        "on": 520.0,
        "CH": 3300.0,
        "LH": 980.0,
        "NH": 760.0,
        "RR": 120.0,
        "SS": 3600.0,
        "X": 2800.0,
    }

    if phoneme in frequencies:
        return frequencies[phoneme]

    if len(phoneme) == 1 and phoneme.isalpha():
        return 180.0 + (ord(phoneme[0]) % 18) * 22.0

    return 0.0
