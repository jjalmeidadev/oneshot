VOWELS = set("aeiouáéíóúâêôãõà")
LIQUIDS = set("lr")


def syllabify_text(text: str) -> list[str]:
    syllables: list[str] = []
    words = text.split()

    for word_index, word in enumerate(words):
        syllables.extend(syllabify_word(word))

        if word_index < len(words) - 1:
            syllables.append(" ")

    return syllables


def syllabify_word(word: str) -> list[str]:
    if not any(char in VOWELS for char in word):
        return [word]

    syllables: list[str] = []
    start = 0

    while start < len(word):
        vowel_start = _find_next_vowel(word, start)

        if vowel_start == -1:
            if syllables:
                syllables[-1] += word[start:]
            else:
                syllables.append(word[start:])
            break

        nucleus_end = _consume_vowel_group(word, vowel_start)
        next_vowel = _find_next_vowel(word, nucleus_end)

        if next_vowel == -1:
            end = len(word)
        else:
            cluster = word[nucleus_end:next_vowel]
            end = _syllable_end(nucleus_end, cluster)

        if end <= start:
            end = nucleus_end

        syllables.append(word[start:end])
        start = end

    return syllables


def _find_next_vowel(word: str, start: int) -> int:
    for index in range(start, len(word)):
        if word[index] in VOWELS:
            return index

    return -1


def _consume_vowel_group(word: str, start: int) -> int:
    end = start + 1

    while end < len(word) and word[end] in VOWELS:
        end += 1

    return end


def _syllable_end(cluster_start: int, consonant_cluster: str) -> int:
    if not consonant_cluster:
        return cluster_start

    if len(consonant_cluster) == 1:
        return cluster_start

    if consonant_cluster[-1] in LIQUIDS:
        return cluster_start + max(0, len(consonant_cluster) - 2)

    return cluster_start + len(consonant_cluster) - 1
