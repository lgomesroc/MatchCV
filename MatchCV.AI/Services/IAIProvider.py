from abc import ABC, abstractmethod

from MatchCV.AI.Models.AIAnalysisResponse import AIAnalysisResponse


class IAIProvider(ABC):
    """Contrato interno para provedores de inteligência artificial."""

    @abstractmethod
    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> AIAnalysisResponse:
        """Executa uma análise de currículo."""
        raise NotImplementedError
