import pytest

from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Validation.ResumeFileValidator import (
    ResumeFileValidator,
)


class TestResumeFileValidator:
    def test_accepts_pdf_file(self):
        ResumeFileValidator.validate(
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

    def test_accepts_doc_file(self):
        ResumeFileValidator.validate(
            file_name="curriculo.doc",
            file_size_bytes=1024,
        )

    def test_accepts_docx_file(self):
        ResumeFileValidator.validate(
            file_name="curriculo.docx",
            file_size_bytes=1024,
        )

    def test_accepts_uppercase_extension(self):
        ResumeFileValidator.validate(
            file_name="CURRICULO.PDF",
            file_size_bytes=1024,
        )

    @pytest.mark.parametrize(
        "file_name",
        [
            "",
            "   ",
            None,
        ],
    )
    def test_rejects_empty_file_name(self, file_name):
        with pytest.raises(
            ParserException,
            match="nome do arquivo",
        ):
            ResumeFileValidator.validate(
                file_name=file_name,
                file_size_bytes=1024,
            )

    @pytest.mark.parametrize(
        "file_size_bytes",
        [
            0,
            -1,
        ],
    )
    def test_rejects_zero_or_negative_file_size(
        self,
        file_size_bytes,
    ):
        with pytest.raises(
            ParserException,
            match="tamanho maior que zero",
        ):
            ResumeFileValidator.validate(
                file_name="curriculo.pdf",
                file_size_bytes=file_size_bytes,
            )

    def test_accepts_file_at_maximum_size(self):
        ResumeFileValidator.validate(
            file_name="curriculo.pdf",
            file_size_bytes=ResumeFileValidator.MAX_FILE_SIZE_BYTES,
        )

    def test_rejects_file_larger_than_one_mb(self):
        with pytest.raises(
            ParserException,
            match="ultrapassar 1 MB",
        ):
            ResumeFileValidator.validate(
                file_name="curriculo.pdf",
                file_size_bytes=(
                    ResumeFileValidator.MAX_FILE_SIZE_BYTES + 1
                ),
            )

    @pytest.mark.parametrize(
        "file_name",
        [
            "curriculo.txt",
            "curriculo.rtf",
            "curriculo",
            "curriculo.pdf.exe",
        ],
    )
    def test_rejects_unsupported_extension(self, file_name):
        with pytest.raises(
            ParserException,
            match="Formato de currículo não suportado",
        ):
            ResumeFileValidator.validate(
                file_name=file_name,
                file_size_bytes=1024,
            )
