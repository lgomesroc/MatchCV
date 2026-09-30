from typing import BinaryIO

from MatchCV.Parser.Interfaces.IResumeParser import IResumeParser
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Exceptions.ParserException import ParserException


class ResumeParserService:
    """Serviço responsável por selecionar o parser adequado ao arquivo."""

    def __init__(
        self,
        pdf_parser: IResumeParser,
        doc_parser: IResumeParser,
        docx_parser: IResumeParser,
    ) -> None:
        self._pdf_parser = pdf_parser
        self._doc_parser = doc_parser
        self._docx_parser = docx_parser

    def parse(
        self,
        file_stream: BinaryIO,
        file_name: str,
        file_size_bytes: int,
    ) -> ParsedResume:
        extension = self._get_extension(file_name)

        if extension == ".pdf":
            parser = self._pdf_parser
        elif extension == ".doc":
            parser = self._doc_parser
        elif extension == ".docx":
            parser = self._docx_parser
        else:
            raise ParserException(
                "Formato de currículo não suportado."
            )

        return parser.parse(
            file_stream=file_stream,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )

    @staticmethod
    def _get_extension(file_name: str) -> str:
        normalized_name = file_name.strip().lower()

        if "." not in normalized_name:
            return ""

        return "." + normalized_name.rsplit(".", 1)[1]
