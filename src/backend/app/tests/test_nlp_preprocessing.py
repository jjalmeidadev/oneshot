"""Pre-processamento textual do pipeline de PLN (Secao 8.10.3 do Projeto.md)."""

import pytest

from app.nlp.preprocessing import (
    REGEX_TOKEN_PATTERN,
    SELECTED_CONFIG,
    preprocess_text,
    tokenize,
    tokenize_all,
)


class TestSelectedConfiguration:
    """A `config_22` e o contrato entre o codigo e o modelo ja treinado."""

    def test_matches_the_configuration_documented_in_the_benchmark(self) -> None:
        assert dict(SELECTED_CONFIG) == {
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

    def test_configuration_is_immutable(self) -> None:
        with pytest.raises(TypeError):
            SELECTED_CONFIG["lowercase"] = False  # type: ignore[index]

    def test_tokenize_applies_the_selected_configuration(self) -> None:
        assert tokenize("Qual é o STATUS?") == preprocess_text(
            "Qual é o STATUS?", **SELECTED_CONFIG
        )


class TestSelectedConfigurationBehaviour:
    def test_lowercases_and_removes_punctuation(self) -> None:
        assert tokenize("Status, Prazo!") == ["status", "praz"]

    def test_keeps_stopwords_that_carry_the_request_type(self) -> None:
        """A Secao 8.10.3 registra que preservar stopwords venceu na grade."""

        tokens = tokenize("qual quando quanto quem")

        assert tokens == ["qual", "quand", "quant", "quem"]

    def test_applies_snowball_stemming_in_portuguese(self) -> None:
        assert tokenize("modernização cronograma projetos") == [
            "moderniz",
            "cronogram",
            "projet",
        ]

    def test_preserves_accented_characters_as_tokens(self) -> None:
        assert "é" in tokenize("qual é o status")

    def test_splits_project_codes_on_the_hyphen(self) -> None:
        """Por isso a extracao de entidades trabalha sobre o texto cru."""

        assert tokenize("PRJ-2031") == ["prj", "2031"]

    def test_tokenize_all_processes_a_batch(self) -> None:
        assert tokenize_all(["custo", "prazo"]) == [["cust"], ["praz"]]

    def test_is_deterministic(self) -> None:
        frase = "compare o Linha 4-Amarela por custo no último trimestre"

        assert tokenize(frase) == tokenize(frase)


class TestConfigurableGrid:
    """As demais opcoes existem para manter o benchmark reproduzivel."""

    def test_removes_stopwords_when_requested(self) -> None:
        tokens = preprocess_text(
            "qual é o status", tokenizer="regex", remove_stopwords=True
        )

        assert "status" in tokens
        assert "o" not in tokens

    def test_keeps_punctuation_tokens_when_not_removing_them(self) -> None:
        tokens = preprocess_text(
            "status, prazo", tokenizer="wordpunct", remove_punctuation=False
        )

        assert "," in tokens

    def test_expands_ngrams_joined_by_underscore(self) -> None:
        tokens = preprocess_text(
            "prazo do projeto", tokenizer="whitespace", ngram_range=(1, 2)
        )

        assert tokens == [
            "prazo",
            "do",
            "projeto",
            "prazo_do",
            "do_projeto",
        ]

    def test_whitespace_tokenizer_does_not_split_hyphenated_codes(self) -> None:
        assert preprocess_text(
            "PRJ-2031", tokenizer="whitespace", remove_punctuation=False
        ) == ["prj-2031"]

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            pytest.param({"tokenizer": "inexistente"}, "Tokenizador", id="tokenizador"),
            pytest.param({"morphology": "inexistente"}, "Normalizacao", id="morfologia"),
            pytest.param(
                {"morphology": "stemming", "stemmer_type": "inexistente"},
                "Stemmer",
                id="stemmer",
            ),
            pytest.param(
                {"morphology": "lemmatization"}, "custom_lemmatizer", id="lematizacao"
            ),
        ],
    )
    def test_rejects_invalid_options(self, kwargs: dict, message: str) -> None:
        with pytest.raises(ValueError, match=message):
            preprocess_text("texto de teste", **kwargs)

    def test_rslp_is_rejected_outside_portuguese(self) -> None:
        with pytest.raises(ValueError, match="RSLP"):
            preprocess_text(
                "text", morphology="stemming", stemmer_type="rslp", language="english"
            )

    def test_accepts_a_custom_lemmatizer_in_portuguese(self) -> None:
        tokens = preprocess_text(
            "projetos",
            tokenizer="regex",
            morphology="lemmatization",
            custom_lemmatizer=lambda token: token.rstrip("s"),
        )

        assert tokens == ["projeto"]
