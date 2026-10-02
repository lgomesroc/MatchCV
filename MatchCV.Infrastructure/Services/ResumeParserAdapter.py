from typing import BinaryIO

from MatchCV.Application.DTOs.ParsedResumeResult import ParsedResumeResult
from MatchCV.Application.Interfaces.IResumeParserService import (
    IResumeParserService,
)
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Services.ResumeParserService import ResumeParserService


class ResumeParserAdapter(IResumeParserService):
    """Adapta o serviço de parsing para o contrato da Application."""

    def __init__(
        self,
        parser_service: ResumeParserService,
    ) -> None:
        self._parser_service = parser_service

    def parse(
        self,
        file_stream: BinaryIO,
        file_name: str,
        file_size_bytes: int,
    ) -> ParsedResumeResult:
        parsed_resume = self._parser_service.parse(
            file_stream=file_stream,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )

        return self._to_result(parsed_resume)

    @staticmethod
    def _to_result(
        parsed_resume: ParsedResume,
    ) -> ParsedResumeResult:
        return ParsedResumeResult(
            file_name=parsed_resume.file_name,
            file_type=parsed_resume.file_type,
            file_size_bytes=parsed_resume.file_size_bytes,
            page_count=parsed_resume.page_count,
            extracted_text=parsed_resume.extracted_text,
            is_text_extractable=parsed_resume.is_text_extractable,
            is_single_column=parsed_resume.is_single_column,
            has_images=parsed_resume.has_images,
            is_password_protected=parsed_resume.is_password_protected,
        )
