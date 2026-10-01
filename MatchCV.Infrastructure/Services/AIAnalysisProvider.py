from MatchCV.AI.Services.AIProviderService import AIProviderService
from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult
from MatchCV.Application.Interfaces.IAnalysisProvider import (
    IAnalysisProvider,
)


class AIAnalysisProvider(IAnalysisProvider):
    """
    Adapter entre o serviço de IA e a camada Application.

    A camada Application trabalha apenas com AnalysisResult
    e não conhece os modelos específicos da camada AI.
    """

    def __init__(
        self,
        ai_provider_service: AIProviderService,
    ) -> None:
        self._ai_provider_service = ai_provider_service

    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> AnalysisResult:
        response = self._ai_provider_service.analyze(
            resume_text=resume_text,
            job_description=job_description,
        )

        return AnalysisResult(
            evidenced_requirements=response.evidenced_requirements,
            unevidenced_requirements=response.unevidenced_requirements,
            gaps=response.gaps,
            resume_issues=response.resume_issues,
            suggestions=response.suggestions,
        )
