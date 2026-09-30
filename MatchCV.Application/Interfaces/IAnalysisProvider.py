from abc import ABC, abstractmethod

from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult


class IAnalysisProvider(ABC):
    """Contrato para provedores de análise por IA."""

    @abstractmethod
    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> AnalysisResult:
        """Analisa o currículo em relação à vaga."""
        raise NotImplementedError
