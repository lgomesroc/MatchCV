from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Models.ParsedResume import ParsedResume


def test_parsed_resume_stores_all_provided_fields():
    file_type = next(iter(FileType))

    parsed_resume = ParsedResume(
        file_name="curriculo.pdf",
        file_type=file_type,
        file_size_bytes=50_000,
        page_count=2,
        extracted_text=(
            "Experiência profissional em desenvolvimento de sistemas "
            "e integração de APIs REST."
        ),
        is_text_extractable=True,
        is_single_column=True,
        has_images=False,
        is_password_protected=False,
    )

    assert parsed_resume.file_name == "curriculo.pdf"
    assert parsed_resume.file_type == file_type
    assert parsed_resume.file_size_bytes == 50_000
    assert parsed_resume.page_count == 2
    assert parsed_resume.is_text_extractable is True
    assert parsed_resume.is_single_column is True
    assert parsed_resume.has_images is False
    assert parsed_resume.is_password_protected is False


def test_parsed_resume_allows_unknown_column_structure():
    parsed_resume = ParsedResume(
        file_name="curriculo.pdf",
        file_type=next(iter(FileType)),
        file_size_bytes=50_000,
        page_count=1,
        extracted_text="Texto extraído do currículo.",
        is_text_extractable=True,
        is_single_column=None,
        has_images=False,
        is_password_protected=False,
    )

    assert parsed_resume.is_single_column is None
