import re
import unicodedata

DIGITS = {
    "0": "zero",
    "1": "um",
    "2": "dois",
    "3": "três",
    "4": "quatro",
    "5": "cinco",
    "6": "seis",
    "7": "sete",
    "8": "oito",
    "9": "nove",
}

NUMBERS_0_TO_99 = {
    0: "zero",
    1: "um",
    2: "dois",
    3: "três",
    4: "quatro",
    5: "cinco",
    6: "seis",
    7: "sete",
    8: "oito",
    9: "nove",
    10: "dez",
    11: "onze",
    12: "doze",
    13: "treze",
    14: "quatorze",
    15: "quinze",
    16: "dezesseis",
    17: "dezessete",
    18: "dezoito",
    19: "dezenove",
    20: "vinte",
    30: "trinta",
    40: "quarenta",
    50: "cinquenta",
    60: "sessenta",
    70: "setenta",
    80: "oitenta",
    90: "noventa",
}

def normalize_text(text: str) -> str:
    text = text.strip()
    text = _normalize_unicode(text)
    text = _replace_percentages(text)
    text = _replace_codes_with_digits(text)
    text = _replace_numbers(text)
    text = _replace_symbols(text)
    text = _remove_unwanted_chars(text)
    text = _collapse_spaces(text)
    return text.lower()


def _normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)

def _replace_percentages(text: str) -> str:
    return re.sub(
        r"\b(\d{1,2})\s?%",
        lambda match: f"{_number_to_words(int(match.group(1)))} por cento",
        text,
    )

def _replace_codes_with_digits(text: str) -> str:
    pattern = r"\b([A-Za-z]{2,})-(\d+)\b"

    def replace(match: re.Match) -> str:
        prefix = match.group(1)
        digits = " ".join(DIGITS[digit] for digit in match.group(2))
        return f"{prefix} {digits}"

    return re.sub(pattern, replace, text)


def _replace_numbers(text: str) -> str:
    return re.sub(
        r"\b\d{1,2}\b",
        lambda match: _number_to_words(int(match.group(0))),
        text,
    )


def _number_to_words(number: int) -> str:
    if number in NUMBERS_0_TO_99:
        return NUMBERS_0_TO_99[number]

    tens = number // 10 * 10
    units = number % 10

    if 20 < number < 100 and units > 0:
        return f"{NUMBERS_0_TO_99[tens]} e {NUMBERS_0_TO_99[units]}"

    return " ".join(DIGITS[digit] for digit in str(number))


def _replace_symbols(text: str) -> str:
    replacements = {
        "&": " e ",
        "@": " arroba ",
        "+": " mais ",
        "=": " igual ",
        "/": " ",
        "-": " ",
    }

    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    return text


def _remove_unwanted_chars(text: str) -> str:
    return re.sub(r"[^A-Za-zÀ-ÿ0-9\s]", " ", text)


def _collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
