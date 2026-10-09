import pytest

from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Validation.ResumeStructureValidator import (
    ResumeStructureValidator,
)
from MatchCV.Domain.Enums.FileType import FileType


VALID_TEXT = (
    "Experiência profissional em desenvolvimento de sistemas, "
    "construção de APIs REST e integração com bancos de dados."
)


def create_valid_parsed_resume(**overrides):
    values = {
        "file_name": "curriculo.pdf",
        "file_type": next(iter(FileType)),
        "file_size_bytes": 50_000,
        "page_count": 2,
        "extracted_text": VALID_TEXT,
        "is_text_extractable": True,
        "is_single_column": True,
        "has_images": False,
        "is_password_protected": False,
    }
    values.update(overrides)

    return ParsedResume(**values)


def test_validate_accepts_valid_resume():
    parsed_resume = create_valid_parsed_resume()

    ResumeStructureValidator.validate(parsed_resume)


def test_validate_accepts_one_page_resume():
    parsed_resume = create_valid_parsed_resume(page_count=1)

    ResumeStructureValidator.validate(parsed_resume)


def test_validate_accepts_resume_with_two_pages():
    parsed_resume = create_valid_parsed_resume(page_count=2)

    ResumeStructureValidator.validate(parsed_resume)


@pytest.mark.parametrize("page_count", [0, -1])
def test_validate_rejects_resume_without_valid_page_count(page_count):
    parsed_resume = create_valid_parsed_resume(
        page_count=page_count,
    )

    with pytest.raises(ParserException):
        ResumeStructureValidator.validate(parsed_resume)


def test_validate_rejects_resume_with_more_than_two_pages():
    parsed_resume = create_valid_parsed_resume(page_count=3)

    with pytest.raises(ParserException):
        ResumeStructureValidator.validate(parsed_resume)


def test_validate_rejects_resume_without_extractable_text():
    parsed_resume = create_valid_parsed_resume(
        is_text_extractable=False,
    )

    with pytest.raises(ParserException):
        ResumeStructureValidator.validate(parsed_resume)


def test_validate_rejects_text_with_fewer_than_30_useful_characters():
    parsed_resume = create_valid_parsed_resume(
        extracted_text="Desenvolvedor com APIs",
    )

    with pytest.raises(ParserException):
        ResumeStructureValidator.validate(parsed_resume)


def test_validate_accepts_text_with_at_least_30_useful_characters():
    parsed_resume = create_valid_parsed_resume(
        extracted_text=VALID_TEXT,
    )

    ResumeStructureValidator.validate(parsed_resume)


def test_validate_rejects_password_protected_resume():
    parsed_resume = create_valid_parsed_resume(
        is_password_protected=True,
    )

    with pytest.raises(ParserException):
        ResumeStructureValidator.validate(parsed_resume)


def test_validate_rejects_multi_column_resume():
    parsed_resume = create_valid_parsed_resume(
        is_single_column=False,
    )

    with pytest.raises(ParserException):
        ResumeStructureValidator.validate(parsed_resume)


def test_validate_accepts_resume_when_column_structure_is_unknown():
    parsed_resume = create_valid_parsed_resume(
        is_single_column=None,
    )

    ResumeStructureValidator.validate(parsed_resume)
