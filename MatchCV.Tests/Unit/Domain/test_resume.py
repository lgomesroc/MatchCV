import pytest

from MatchCV.Domain.Entities.Resume import Resume
from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Domain.Exceptions.DomainException import DomainException


VALID_TEXT = (
    "Experiência profissional em desenvolvimento de sistemas, "
    "construção de APIs REST e integração com bancos de dados."
)


def create_valid_resume(**overrides):
    values = {
        "file_name": "curriculo.pdf",
        "file_type": next(iter(FileType)),
        "file_size_bytes": 50_000,
        "page_count": 2,
        "extracted_text": VALID_TEXT,
    }
    values.update(overrides)

    return Resume.create(**values)


def test_create_returns_resume_with_expected_values():
    result = create_valid_resume()

    assert result.id is not None
    assert result.file_name == "curriculo.pdf"
    assert result.file_type == next(iter(FileType))
    assert result.file_size_bytes == 50_000
    assert result.page_count == 2
    assert result.extracted_text == VALID_TEXT


def test_create_trims_file_name_and_extracted_text():
    result = create_valid_resume(
        file_name="  curriculo.pdf  ",
        extracted_text=f"  {VALID_TEXT}  ",
    )

    assert result.file_name == "curriculo.pdf"
    assert result.extracted_text == VALID_TEXT


@pytest.mark.parametrize(
    "file_name",
    [
        None,
        "",
        "   ",
    ],
)
def test_create_rejects_missing_file_name(file_name):
    with pytest.raises(DomainException):
        create_valid_resume(file_name=file_name)


@pytest.mark.parametrize(
    "file_size_bytes",
    [
        0,
        -1,
    ],
)
def test_create_rejects_non_positive_file_size(file_size_bytes):
    with pytest.raises(DomainException):
        create_valid_resume(file_size_bytes=file_size_bytes)


def test_create_rejects_file_larger_than_one_megabyte():
    with pytest.raises(DomainException):
        create_valid_resume(
            file_size_bytes=Resume.MAX_FILE_SIZE_BYTES + 1
        )


def test_create_accepts_file_at_maximum_size():
    result = create_valid_resume(
        file_size_bytes=Resume.MAX_FILE_SIZE_BYTES
    )

    assert result.file_size_bytes == Resume.MAX_FILE_SIZE_BYTES


@pytest.mark.parametrize(
    "page_count",
    [
        0,
        -1,
    ],
)
def test_create_rejects_invalid_page_count(page_count):
    with pytest.raises(DomainException):
        create_valid_resume(page_count=page_count)


def test_create_rejects_more_than_two_pages():
    with pytest.raises(DomainException):
        create_valid_resume(page_count=3)


def test_create_accepts_one_page():
    result = create_valid_resume(page_count=1)

    assert result.page_count == 1


@pytest.mark.parametrize(
    "extracted_text",
    [
        None,
        "",
        "   ",
    ],
)
def test_create_rejects_missing_extracted_text(extracted_text):
    with pytest.raises(DomainException):
        create_valid_resume(extracted_text=extracted_text)


def test_create_rejects_text_with_fewer_than_30_useful_characters():
    with pytest.raises(DomainException):
        create_valid_resume(
            extracted_text="Desenvolvedor com APIs"
        )


def test_create_rejects_inappropriate_content():
    with pytest.raises(DomainException):
        create_valid_resume(
            extracted_text=(
                "Experiência profissional em desenvolvimento, "
                "construção de APIs REST e uso de fuck."
            )
        )


def test_create_generates_distinct_identifiers():
    first = create_valid_resume()
    second = create_valid_resume()

    assert first.id != second.id
