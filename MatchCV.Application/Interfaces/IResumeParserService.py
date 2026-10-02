from abc import ABC, abstractmethod
from typing import BinaryIO

from MatchCV.Application.DTOs.ParsedResumeResult import ParsedResumeResult


class IResumeParserService(ABC):
    """
    Contrato da aplicação para processamento de currículos.

    A camada Application conhece apenas este contrato e o DTO de
    resultado. A implementação concreta fica fora da Application.
    """

    @abstractmethod
    def parse(
        self,
        file_stream: BinaryIO,
        file_name: str,
        file_size_bytes: int,
    ) -> ParsedResumeResult:
        """
        Processa um currículo e retorna os dados necessários
        para a análise.
        """
        raise NotImplementedError
