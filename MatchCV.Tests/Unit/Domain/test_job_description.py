import pytest

from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Domain.Exceptions.DomainException import DomainException


VALID_DESCRIPTION = (
    "Desenvolvimento de sistemas, manutenção de APIs, "
    "integração com bancos de dados e testes automatizados."
)


def test_create_returns_job_description_with_uuid_and_content():
    result = JobDescription.create(VALID_DESCRIPTION)

    assert result.id is not None
    assert result.content == VALID_DESCRIPTION


def test_create_trims_whitespace_at_the_edges():
    result = JobDescription.create(
        f"  {VALID_DESCRIPTION}  "
    )

    assert result.content == VALID_DESCRIPTION


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
    ],
)
def test_create_rejects_missing_or_blank_content(value):
    with pytest.raises(DomainException):
        JobDescription.create(value)


def test_create_rejects_content_with_fewer_than_30_useful_characters():
    with pytest.raises(DomainException):
        JobDescription.create("Desenvolvedor com APIs")


def test_create_rejects_content_longer_than_3000_characters():
    with pytest.raises(DomainException):
        JobDescription.create("A" * 3001)


def test_create_accepts_content_at_the_maximum_length():
    content = "A" * JobDescription.MAX_CHARACTERS

    result = JobDescription.create(content)

    assert len(result.content) == JobDescription.MAX_CHARACTERS


@pytest.mark.parametrize(
    "value",
    [
        "123456789012345678901234567890",
        "!@#$%^&*()!@#$%^&*()!@#$%^&*()",
        "Desenvolvedor Python 😀 com experiência",
        "Desenvolvedor Python com experiência :)",
    ],
)
def test_create_rejects_invalid_content(value):
    with pytest.raises(DomainException):
        JobDescription.create(value)


def test_create_rejects_inappropriate_content():
    description = (
        "Desenvolvimento de sistemas, integração de APIs, "
        "testes automatizados e uso de tecnologia fuck."
    )

    with pytest.raises(DomainException):
        JobDescription.create(description)


def test_create_generates_distinct_identifiers():
    first = JobDescription.create(VALID_DESCRIPTION)
    second = JobDescription.create(VALID_DESCRIPTION)

    assert first.id != second.id
