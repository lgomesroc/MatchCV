from io import BytesIO
from unittest.mock import Mock

import pytest

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Interfaces.IResumeParser import IResumeParser
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Services.ResumeParserService import (
    ResumeParserService,
)


VALID_TEXT = (
    "Experiência profissional em desenvolvimento de sistemas, "
    "construção de APIs REST e integração com bancos de dados."
)


def create_valid_parsed_resume(file_name="curriculo.pdf"):
    return ParsedResume(
        file_name=file_name,
        file_type=next(iter(FileType)),
        file_size_bytes=50_000,
        page_count=2,
        extracted_text=VALID_TEXT,
        is_text_extractable=True,
        is_single_column=True,
        has_images=False,
        is_password_protected=False,
    )


def create_service():
    pdf_parser = Mock(spec=IResumeParser)
    doc_parser = Mock(spec=IResumeParser)
    docx_parser = Mock(spec=IResumeParser)

    service = ResumeParserService(
        pdf_parser=pdf_parser,
        doc_parser=doc_parser,
        docx_parser=docx_parser,
    )

    return service, pdf_parser, doc_parser, docx_parser


@pytest.mark.parametrize(
    ("file_name", "parser_position"),
    [
        ("curriculo.pdf", 1),
        ("curriculo.doc", 2),
        ("curriculo.docx", 3),
    ],
)
def test_parse_selects_parser_based_on_extension(
    file_name,
    parser_position,
):
    service, pdf_parser, doc_parser, docx_parser = create_service()

    parsers = [pdf_parser, doc_parser, docx_parser]
    selected_parser = parsers[parser_position - 1]

    parsed_resume = create_valid_parsed_resume(file_name=file_name)
    selected_parser.parse.return_value = parsed_resume

    file_stream = BytesIO(b"conteudo de teste")

    result = service.parse(
        file_stream=file_stream,
        file_name=file_name,
        file_size_bytes=50_000,
    )

    assert result is parsed_resume
    selected_parser.parse.assert_called_once_with(
        file_stream=file_stream,
        file_name=file_name,
        file_size_bytes=50_000,
    )

    for parser in parsers:
        if parser is not selected_parser:
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
def test_parse_rejects_unsupported_file_extension(file_name):
    service, pdf_parser, doc_parser, docx_parser = create_service()

    with pytest.raises(ParserException):
        service.parse(
            file_stream=BytesIO(b"conteudo de teste"),
            file_name=file_name,
            file_size_bytes=50_000,
        )

    pdf_parser.parse.assert_not_called()
    doc_parser.parse.assert_not_called()
    docx_parser.parse.assert_not_called()


@pytest.mark.parametrize(
    "file_name",
    [
        "CURRICULO.PDF",
        "Curriculo.Pdf",
    ],
)
def test_parse_accepts_uppercase_pdf_extension(file_name):
    service, pdf_parser, _, _ = create_service()

    parsed_resume = create_valid_parsed_resume(file_name=file_name)
    pdf_parser.parse.return_value = parsed_resume

    result = service.parse(
        file_stream=BytesIO(b"conteudo de teste"),
        file_name=file_name,
        file_size_bytes=50_000,
    )

    assert result is parsed_resume
    pdf_parser.parse.assert_called_once()


def test_parse_rejects_result_with_invalid_structure():
    service, pdf_parser, _, _ = create_service()

    invalid_resume = create_valid_parsed_resume()
    invalid_resume.page_count = 3
    pdf_parser.parse.return_value = invalid_resume

    with pytest.raises(ParserException):
        service.parse(
            file_stream=BytesIO(b"conteudo de teste"),
            file_name="curriculo.pdf",
            file_size_bytes=50_000,
        )


def test_parse_returns_result_after_successful_validation():
    service, pdf_parser, _, _ = create_service()

    parsed_resume = create_valid_parsed_resume()
    pdf_parser.parse.return_value = parsed_resume

    result = service.parse(
        file_stream=BytesIO(b"conteudo de teste"),
        file_name="curriculo.pdf",
        file_size_bytes=50_000,
    )

    assert result == parsed_resume


def test_parse_propagates_parser_exception():
    service, pdf_parser, _, _ = create_service()

    pdf_parser.parse.side_effect = ParserException(
        "Falha ao interpretar o documento."
    )

    with pytest.raises(
        ParserException,
        match="Falha ao interpretar o documento.",
    ):
        service.parse(
            file_stream=BytesIO(b"conteudo de teste"),
            file_name="curriculo.pdf",
            file_size_bytes=50_000,
        )
