import pytest

from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Domain.Validation.TextContentValidator import (
    TextContentValidator,
)


def test_normalize_whitespace_collapses_spaces_tabs_and_newlines():
    result = TextContentValidator.normalize_whitespace(
        "  Desenvolvedor   backend\tcom\nexperiência  "
    )

    assert result == " Desenvolvedor backend com experiência "


def test_validate_required_returns_trimmed_normalized_text():
    result = TextContentValidator.validate_required(
        "  Desenvolvedor   backend  ",
        "O campo",
    )

    assert result == "Desenvolvedor backend"


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "\t\n  ",
    ],
)
def test_validate_required_rejects_missing_or_blank_values(value):
    with pytest.raises(DomainException):
        TextContentValidator.validate_required(value, "O campo")


def test_validate_not_only_numbers_rejects_numeric_content():
    with pytest.raises(DomainException):
        TextContentValidator.validate_not_only_numbers(
            "123 456",
            "O campo",
        )


def test_validate_not_only_numbers_accepts_text_containing_numbers():
    TextContentValidator.validate_not_only_numbers(
        "Desenvolvedor Python 3",
        "O campo",
    )


def test_validate_not_only_special_characters_rejects_symbols():
    with pytest.raises(DomainException):
        TextContentValidator.validate_not_only_special_characters(
            "!@#$%",
            "O campo",
        )


def test_validate_not_only_special_characters_accepts_alphanumeric_text():
    TextContentValidator.validate_not_only_special_characters(
        "API REST!",
        "O campo",
    )


def test_validate_first_character_rejects_special_character():
    with pytest.raises(DomainException):
        TextContentValidator.validate_first_character(
            "@Desenvolvedor",
            "O campo",
        )


def test_validate_first_character_allows_dot_when_configured():
    TextContentValidator.validate_first_character(
        ".NET Developer",
        "O campo",
        allow_dot=True,
    )


def test_validate_first_character_rejects_dot_by_default():
    with pytest.raises(DomainException):
        TextContentValidator.validate_first_character(
            ".Nome",
            "O campo",
        )


def test_validate_no_consecutive_special_characters_rejects_symbols():
    with pytest.raises(DomainException):
        TextContentValidator.validate_no_consecutive_special_characters(
            "Nome@@Silva",
            "O campo",
        )


def test_validate_no_consecutive_special_characters_accepts_single_separator():
    TextContentValidator.validate_no_consecutive_special_characters(
        "Ana-Silva",
        "O campo",
    )


@pytest.mark.parametrize(
    "value",
    [
        "Desenvolvedor Python 😀",
        "Desenvolvedor feliz :)",
        "Desenvolvedor triste :(",
        "Desenvolvedor feliz ;)",
        "Desenvolvedor feliz xD",
        "Desenvolvedor <3",
    ],
)
def test_validate_no_emoji_or_emoticon_rejects_emoji_and_emoticons(value):
    with pytest.raises(DomainException):
        TextContentValidator.validate_no_emoji_or_emoticon(
            value,
            "O campo",
        )


def test_validate_no_emoji_or_emoticon_accepts_normal_text():
    TextContentValidator.validate_no_emoji_or_emoticon(
        "Desenvolvedor Python com experiência em APIs REST",
        "O campo",
    )


def test_validate_name_returns_normalized_name():
    result = TextContentValidator.validate_name(
        "  Ana   Silva  "
    )

    assert result == "Ana Silva"


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "123456",
        "!@#$%",
        "@Ana",
        "Ana@@Silva",
    ],
)
def test_validate_name_rejects_invalid_names(value):
    with pytest.raises(DomainException):
        TextContentValidator.validate_name(value)


def test_validate_job_description_returns_normalized_text():
    result = TextContentValidator.validate_job_description(
        "  Desenvolvedor   backend com experiência  "
    )

    assert result == "Desenvolvedor backend com experiência"


def test_validate_job_description_allows_dot_as_first_character():
    result = TextContentValidator.validate_job_description(
        ".NET Developer com experiência em APIs"
    )

    assert result.startswith(".NET")


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "123456",
        "!@#$%",
        "@Desenvolvedor",
        "Desenvolvedor Python 😀",
        "Desenvolvedor Python :)",
    ],
)
def test_validate_job_description_rejects_invalid_content(value):
    with pytest.raises(DomainException):
        TextContentValidator.validate_job_description(value)