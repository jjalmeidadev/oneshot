"""Pre-processamento textual do pipeline de PLN.

A funcao ``preprocess_text`` e a mesma usada no benchmark do notebook
[`classificador_intencoes_metro.ipynb`](../../../notebooks/classificador_intencoes_metro.ipynb),
portada para modulo importavel conforme o RNF10. **Nao altere o comportamento
dela sem reexecutar o benchmark**: os vetorizadores TF-IDF serializados em
`src/notebooks/artefatos/classificador_intencoes.joblib` foram ajustados sobre
os tokens que ela produz, e qualquer mudanca de tokenizacao ou de radical
invalida o modelo treinado.

``SELECTED_CONFIG`` e a `config_22`, escolhida por validacao cruzada agrupada
entre 36 configuracoes de pre-processamento (72 combinacoes contando os dois
classificadores da grade) e registrada na Secao 8.10.3 de `docs/Projeto.md`.
Nela as stopwords sao **preservadas**, porque palavras como "qual", "quando",
"quanto" e "quem" distinguem tipos de solicitacao.

A configuracao selecionada nao exige nenhum corpus baixado do NLTK: o
tokenizador e uma expressao regular e o Snowball e algoritmico. As demais
opcoes da grade — mantidas para que o benchmark continue reproduzivel — podem
exigir `nltk.download('punkt')` e `nltk.download('stopwords')`.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Callable, Iterable, Sequence

from nltk.stem import RSLPStemmer, SnowballStemmer
from nltk.tokenize import RegexpTokenizer, WhitespaceTokenizer, wordpunct_tokenize

# Padrao que preserva caracteres acentuados e descarta separadores.
REGEX_TOKEN_PATTERN = r"[^\W_]+"

# config_22 da Secao 8.10.3: a configuracao vencedora da grade.
SELECTED_CONFIG = MappingProxyType(
    {
        "lowercase": True,
        "tokenizer": "regex",
        "remove_stopwords": False,
        "remove_punctuation": True,
        "morphology": "stemming",
        "stemmer_type": "snowball",
        "ngram_range": None,
        "language": "portuguese",
        "regex_pattern": REGEX_TOKEN_PATTERN,
    }
)

_STEMMER_CACHE: dict[tuple[str, str], object] = {}


def preprocess_text(
    text: str,
    lowercase: bool = True,
    tokenizer: str = "word",
    remove_stopwords: bool = False,
    remove_punctuation: bool = True,
    morphology: str = "none",
    stemmer_type: str = "snowball",
    ngram_range: tuple[int, int] | None = None,
    language: str = "portuguese",
    regex_pattern: str = r"\w+",
    custom_lemmatizer: Callable[[str], str] | None = None,
) -> list[str]:
    """Pre-processamento configuravel para experimentos de PLN.

    tokenizer   : "word" | "wordpunct" | "whitespace" | "regex"
    morphology  : "none" | "stemming" | "lemmatization"
    stemmer_type: "snowball" | "rslp"
    ngram_range : None | (1,1) | (1,2) | (1,3) | (2,2) ...
    """

    if lowercase:
        text = text.lower()

    tokens = _tokenize(text, tokenizer, language, regex_pattern)

    if remove_punctuation:
        tokens = [token for token in tokens if token.isalnum()]

    if remove_stopwords:
        tokens = [token for token in tokens if token not in _stopwords(language)]

    if morphology == "stemming":
        stemmer = _stemmer(stemmer_type, language)
        tokens = [stemmer.stem(token) for token in tokens]
    elif morphology == "lemmatization":
        tokens = _lemmatize(tokens, language, custom_lemmatizer)
    elif morphology != "none":
        raise ValueError(f"Normalizacao invalida: {morphology}")

    if ngram_range is not None:
        tokens = _expand_ngrams(tokens, ngram_range)

    return tokens


def tokenize(text: str) -> list[str]:
    """Aplica a configuracao selecionada, que e a usada em producao."""

    return preprocess_text(text, **SELECTED_CONFIG)


def tokenize_all(texts: Iterable[str]) -> list[list[str]]:
    """Versao em lote de ``tokenize``, para vetorizacao de varios textos."""

    return [tokenize(text) for text in texts]


def _tokenize(
    text: str, tokenizer: str, language: str, regex_pattern: str
) -> list[str]:
    if tokenizer == "word":
        # Importado sob demanda: exige o corpus 'punkt' do NLTK, que a
        # configuracao selecionada nao utiliza.
        from nltk.tokenize import word_tokenize

        return word_tokenize(text, language=language)
    if tokenizer == "wordpunct":
        return wordpunct_tokenize(text)
    if tokenizer == "whitespace":
        return WhitespaceTokenizer().tokenize(text)
    if tokenizer == "regex":
        return RegexpTokenizer(regex_pattern).tokenize(text)

    raise ValueError(f"Tokenizador invalido: {tokenizer}")


def _stopwords(language: str) -> set[str]:
    from nltk.corpus import stopwords

    return set(stopwords.words(language))


def _stemmer(stemmer_type: str, language: str):
    """Reaproveita o stemmer entre chamadas; instancia-lo e caro."""

    key = (stemmer_type, language)
    if key in _STEMMER_CACHE:
        return _STEMMER_CACHE[key]

    if stemmer_type == "snowball":
        stemmer = SnowballStemmer(language)
    elif stemmer_type == "rslp":
        if language != "portuguese":
            raise ValueError("RSLP e especifico para portugues.")
        stemmer = RSLPStemmer()
    else:
        raise ValueError(f"Stemmer invalido: {stemmer_type}")

    _STEMMER_CACHE[key] = stemmer
    return stemmer


def _lemmatize(
    tokens: Sequence[str], language: str, custom_lemmatizer: Callable[[str], str] | None
) -> list[str]:
    if custom_lemmatizer is not None:
        return [custom_lemmatizer(token) for token in tokens]
    if language == "english":
        from nltk.stem import WordNetLemmatizer

        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token) for token in tokens]

    raise ValueError("Para portugues, forneca um custom_lemmatizer.")


def _expand_ngrams(tokens: Sequence[str], ngram_range: tuple[int, int]) -> list[str]:
    min_n, max_n = ngram_range
    resultado: list[str] = []
    for n in range(min_n, max_n + 1):
        if n == 1:
            resultado.extend(tokens)
            continue
        resultado.extend(
            "_".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)
        )
    return resultado
