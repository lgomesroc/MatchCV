
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Interfaces.IResumeParser import IResumeParser
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Services.ResumeParserService import ResumeParserService


VALID_RESUME_TEXT = (
    "Experiencia profissional em desenvolvimento de sistemas "
    "com Python, APIs REST, bancos de dados e testes automatizados."
)


def create_parsed_resume(**overrides) -> ParsedResume:
    values = {
        "file_name": "curriculo.pdf",
        "file_type": next(iter(FileType)),
        "file_size_bytes": 1024,
        "page_count": 1,
        "extracted_text": VALID_RESUME_TEXT,
        "is_text_extractable": True,
        "is_single_column": True,
        "has_images": False,
        "is_password_protected": False,
    }

    values.update(overrides)

    return ParsedResume(**values)


def create_service(parsed_resume: ParsedResume):
    pdf_parser = MagicMock(spec=IResumeParser)
    doc_parser = MagicMock(spec=IResumeParser)
    docx_parser = MagicMock(spec=IResumeParser)

    for parser in (pdf_parser, doc_parser, docx_parser):
        parser.parse.return_value = parsed_resume

    service = ResumeParserService(
        pdf_parser=pdf_parser,
        doc_parser=doc_parser,
        docx_parser=docx_parser,
    )

    return service, pdf_parser, doc_parser, docx_parser


class TestResumeParsingPipeline:
    @pytest.mark.parametrize(
        ("file_name", "selected_parser"),
        [
            ("curriculo.pdf", "pdf"),
            ("curriculo.doc", "doc"),
            ("curriculo.docx", "docx"),
            ("CURRICULO.PDF", "pdf"),
            ("Curriculo.DOC", "doc"),
            ("Curriculo.DOCX", "docx"),
        ],
    )
    def test_selects_parser_by_extension(
        self,
        file_name: str,
        selected_parser: str,
    ):
        parsed_resume = create_parsed_resume(
            file_name=file_name,
        )

        service, pdf_parser, doc_parser, docx_parser = (
            create_service(parsed_resume)
        )

        file_stream = BytesIO(b"conteudo de teste")
        file_size_bytes = 1024

        result = service.parse(
            file_stream=file_stream,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )

        assert result is parsed_resume

        parsers = {
            "pdf": pdf_parser,
            "doc": doc_parser,
            "docx": docx_parser,
        }

        parsers[selected_parser].parse.assert_called_once_with(
            file_stream=file_stream,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )

        for name, parser in parsers.items():
            if name != selected_parser:
                parser.parse.assert_not_called()

    @pytest.mark.parametrize(
        "file_name",
        [
            "curriculo.txt",
            "curriculo.rtf",
            "curriculo",
            "",
            "curriculo.pdf.exe",
        ],
    )
    def test_rejects_unsupported_file_extensions(
        self,
        file_name: str,
    ):
        service, pdf_parser, doc_parser, docx_parser = (
            create_service(create_parsed_resume())
        )

        with pytest.raises(
            ParserException,
            match="Formato de currículo não suportado",
        ):
            service.parse(
                file_stream=BytesIO(b"conteudo"),
                file_name=file_name,
                file_size_bytes=1024,
            )

        pdf_parser.parse.assert_not_called()
        doc_parser.parse.assert_not_called()
        docx_parser.parse.assert_not_called()

    @pytest.mark.parametrize(
        ("overrides", "expected_message"),
        [
            (
                {"page_count": 0},
                "pelo menos uma página",
            ),
            (
                {"page_count": 3},
                "mais de duas páginas",
            ),
            (
                {"is_text_extractable": False},
                "Não foi possível extrair texto",
            ),
            (
                {"extracted_text": "abc 123"},
                "30 caracteres úteis",
            ),
            (
                {"is_password_protected": True},
                "protegido por senha",
            ),
            (
                {"is_single_column": False},
                "coluna única",
            ),
        ],
    )
    def test_rejects_resume_that_fails_structure_validation(
        self,
        overrides: dict,
        expected_message: str,
    ):
        parsed_resume = create_parsed_resume(**overrides)

        service, pdf_parser, _, _ = create_service(
            parsed_resume,
        )

        with pytest.raises(
            ParserException,
            match=expected_message,
        ):
            service.parse(
                file_stream=BytesIO(b"conteudo"),
                file_name="curriculo.pdf",
                file_size_bytes=1024,
            )

        pdf_parser.parse.assert_called_once()

    def test_accepts_resume_with_valid_structure(self):
        parsed_resume = create_parsed_resume()

        service, pdf_parser, _, _ = create_service(
            parsed_resume,
        )

        result = service.parse(
            file_stream=BytesIO(b"conteudo"),
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

        assert result is parsed_resume
        assert result.page_count == 1
        assert result.is_text_extractable is True
        assert result.is_single_column is True
        assert result.is_password_protected is False

        pdf_parser.parse.assert_called_once()
