from abc import ABC, abstractmethod
from typing import BinaryIO

from MatchCV.Parser.Models.ParsedResume import ParsedResume


class IResumeParser(ABC):
    """Contrato para parsers de currículo."""

    @abstractmethod
    def parse(
        self,
        file_stream: BinaryIO,
        file_name: str,
        file_size_bytes: int,
    ) -> ParsedResume:
        """Processa um currículo e retorna seus dados estruturados."""
        raise NotImplementedError
