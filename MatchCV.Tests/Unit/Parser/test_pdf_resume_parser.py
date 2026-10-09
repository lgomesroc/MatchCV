from io import BytesIO
from unittest.mock import MagicMock

import pytest

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Parsers import PdfResumeParser as pdf_module
from MatchCV.Parser.Parsers.PdfResumeParser import PdfResumeParser


def create_page(text="", resources=None):
    page = MagicMock()
    page.extract_text.return_value = text
    page.get.return_value = resources or {}
    return page


def create_reader(pages, is_encrypted=False):
    reader = MagicMock()
    reader.is_encrypted = is_encrypted
    reader.pages = pages
    return reader


class TestPdfResumeParser:
    def setup_method(self):
        self.parser = PdfResumeParser()

    def test_extracts_text_from_pdf(self, monkeypatch):
        reader = create_reader(
            [
                create_page("Luciano Rocha"),
                create_page("Desenvolvedor de software"),
            ]
        )
        monkeypatch.setattr(
            pdf_module,
            "PdfReader",
            lambda stream: reader,
        )

        result = self.parser.parse(
            file_stream=BytesIO(b"fake pdf content"),
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

        assert result.file_name == "curriculo.pdf"
        assert result.file_type == FileType.PDF
        assert result.file_size_bytes == 1024
        assert result.page_count == 2
        assert result.extracted_text == (
            "Luciano Rocha\nDesenvolvedor de software"
        )
        assert result.is_text_extractable is True
        assert result.is_single_column is True
        assert result.has_images is False
        assert result.is_password_protected is False

    def test_returns_empty_text_for_encrypted_pdf(
        self,
        monkeypatch,
    ):
        reader = create_reader(
            pages=[],
            is_encrypted=True,
        )
        monkeypatch.setattr(
            pdf_module,
            "PdfReader",
            lambda stream: reader,
        )

        result = self.parser.parse(
            file_stream=BytesIO(b"encrypted pdf"),
            file_name="protegido.pdf",
            file_size_bytes=1024,
        )

        assert result.file_type == FileType.PDF
        assert result.page_count == 0
        assert result.extracted_text == ""
        assert result.is_text_extractable is False
        assert result.is_single_column is None
        assert result.has_images is False
        assert result.is_password_protected is True

    def test_raises_when_pdf_cannot_be_opened(
        self,
        monkeypatch,
    ):
        def raise_reader_error(stream):
            raise ValueError("invalid pdf")

        monkeypatch.setattr(
            pdf_module,
            "PdfReader",
            raise_reader_error,
        )

        with pytest.raises(
            ParserException,
            match="Não foi possível ler o arquivo PDF",
        ):
            self.parser.parse(
                file_stream=BytesIO(b"invalid"),
                file_name="curriculo.pdf",
                file_size_bytes=1024,
            )

    def test_raises_when_text_extraction_fails(
        self,
        monkeypatch,
    ):
        page = create_page()
        page.extract_text.side_effect = ValueError(
            "extraction failed"
        )
        reader = create_reader([page])

        monkeypatch.setattr(
            pdf_module,
            "PdfReader",
            lambda stream: reader,
        )

        with pytest.raises(
            ParserException,
            match="Não foi possível extrair o texto",
        ):
            self.parser.parse(
                file_stream=BytesIO(b"fake pdf"),
                file_name="curriculo.pdf",
                file_size_bytes=1024,
            )

    def test_detects_images_from_page_resources(
        self,
        monkeypatch,
    ):
        page = create_page(
            "Currículo com imagem",
            resources={"/XObject": {"image": object()}},
        )
        reader = create_reader([page])

        monkeypatch.setattr(
            pdf_module,
            "PdfReader",
            lambda stream: reader,
        )

        result = self.parser.parse(
            file_stream=BytesIO(b"fake pdf"),
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

        assert result.has_images is True

    def test_marks_text_as_not_extractable_when_empty(
        self,
        monkeypatch,
    ):
        reader = create_reader(
            [
                create_page(""),
                create_page("   "),
            ]
        )
        monkeypatch.setattr(
            pdf_module,
            "PdfReader",
            lambda stream: reader,
        )

        result = self.parser.parse(
            file_stream=BytesIO(b"fake pdf"),
            file_name="sem-texto.pdf",
            file_size_bytes=1024,
        )

        assert result.extracted_text == ""
        assert result.is_text_extractable is False

    def test_detects_suspicious_multicolumn_layout(self):
        text = (
            "Linha com    espaços\n"
            "Outra linha com    espaços\n"
            "Terceira linha com    espaços"
        )

        result = PdfResumeParser._detect_single_column([text])

        assert result is False

    def test_accepts_text_without_suspicious_columns(self):
        result = PdfResumeParser._detect_single_column(
            ["Nome do candidato\nExperiência profissional"]
        )

        assert result is True

    def test_returns_none_when_there_are_no_pages(self):
        result = PdfResumeParser._detect_single_column([])

        assert result is None
