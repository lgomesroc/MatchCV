import pytest

from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Domain.Validation.ProfanityValidator import (
    ProfanityValidator,
)


@pytest.mark.parametrize(
    "value",
    [
        "Este texto contém fuck.",
        "Este texto contém shit.",
        "Este texto contém caralho.",
        "Este texto contém porra.",
    ],
)
def test_validate_rejects_default_inappropriate_terms(value):
    with pytest.raises(DomainException):
        ProfanityValidator.validate(value, "O campo")


@pytest.mark.parametrize(
    "value",
    [
        "Este texto contém f.u.c.k.",
        "Este texto contém sh1t.",
    ],
)
def test_validate_detects_obfuscated_terms(value):
    with pytest.raises(DomainException):
        ProfanityValidator.validate(value, "O campo")


def test_validate_is_case_insensitive():
    with pytest.raises(DomainException):
        ProfanityValidator.validate(
            "Este texto contém FUCK.",
            "O campo",
        )


def test_validate_ignores_term_inside_a_larger_word():
    ProfanityValidator.validate(
        "O candidato possui experiência como assistente.",
        "O campo",
    )


def test_validate_accepts_normal_professional_text():
    ProfanityValidator.validate(
        "Desenvolvedor backend com experiência em Python, "
        "APIs REST, SQL e testes automatizados.",
        "O campo",
    )


def test_validate_accepts_none():
    assert ProfanityValidator.validate(None, "O campo") is None


def test_validate_supports_custom_terms():
    with pytest.raises(DomainException):
        ProfanityValidator.validate(
            "Este texto contém proibido.",
            "O campo",
            terms={"proibido"},
        )


def test_validate_custom_terms_replace_default_terms():
    ProfanityValidator.validate(
        "Este texto contém fuck.",
        "O campo",
        terms={"termo_especifico"},
    )


def test_normalize_removes_accents_and_normalizes_separators():
    result = ProfanityValidator._normalize("CAFÉ---Teste")

    assert result == "cafe teste"


def test_contains_term_requires_word_boundaries():
    assert ProfanityValidator._contains_term(
        "assistente técnico",
        "ass",
    ) is False

    assert ProfanityValidator._contains_term(
        "palavra proibida aqui",
        "proibida",
    ) is True
