
from MatchCV.Application.DTOs.ParsedResumeResult import ParsedResumeResult
from MatchCV.Domain.Enums.FileType import FileType


class TestParsedResumeResult:
    def test_creates_result_with_all_fields(self):
        result = ParsedResumeResult(
            file_name="curriculo.pdf",
            file_type=FileType.PDF,
            file_size_bytes=2048,
            page_count=2,
            extracted_text="Experiência profissional com desenvolvimento de sistemas.",
            is_text_extractable=True,
            is_single_column=True,
            has_images=False,
            is_password_protected=False,
        )

        assert result.file_name == "curriculo.pdf"
        assert result.file_type == FileType.PDF
        assert result.file_size_bytes == 2048
        assert result.page_count == 2
        assert result.extracted_text == (
            "Experiência profissional com desenvolvimento de sistemas."
        )
        assert result.is_text_extractable is True
        assert result.is_single_column is True
        assert result.has_images is False
        assert result.is_password_protected is False

    def test_preserves_result_for_resume_with_images(self):
        result = ParsedResumeResult(
            file_name="curriculo.docx",
            file_type=FileType.DOCX,
            file_size_bytes=4096,
            page_count=1,
            extracted_text="Experiência profissional com desenvolvimento de sistemas.",
            is_text_extractable=True,
            is_single_column=True,
            has_images=True,
            is_password_protected=False,
        )

        assert result.has_images is True

    def test_preserves_result_for_non_extractable_text(self):
        result = ParsedResumeResult(
            file_name="curriculo.pdf",
            file_type=FileType.PDF,
            file_size_bytes=1024,
            page_count=1,
            extracted_text="",
            is_text_extractable=False,
            is_single_column=True,
            has_images=False,
            is_password_protected=False,
        )

        assert result.extracted_text == ""
        assert result.is_text_extractable is False

    def test_preserves_password_protection_status(self):
        result = ParsedResumeResult(
            file_name="protegido.pdf",
            file_type=FileType.PDF,
            file_size_bytes=1024,
            page_count=1,
            extracted_text="",
            is_text_extractable=False,
            is_single_column=True,
            has_images=False,
            is_password_protected=True,
        )

        assert result.is_password_protected is True
