from typing import BinaryIO

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Parser.Exceptions.ParserException import ParserException
from MatchCV.Parser.Interfaces.IResumeParser import IResumeParser
from MatchCV.Parser.Models.ParsedResume import ParsedResume
from MatchCV.Parser.Validation.ResumeFileValidator import (
    ResumeFileValidator,
)


class DocResumeParser(IResumeParser):
    """
    Parser para documentos DOC legados.

    O formato .doc é o formato binário antigo do Microsoft Word.
    A biblioteca python-docx não suporta esse formato.
    """

    def parse(
        self,
        file_stream: BinaryIO,
        file_name: str,
        file_size_bytes: int,
    ) -> ParsedResume:
        ResumeFileValidator.validate(
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )

        raise ParserException(
            "Arquivos DOC legados não podem ser processados "
            "diretamente nesta versão. Converta o arquivo para "
            "DOCX ou PDF."
        )
