from MatchCV.AI.Exceptions.AIProviderException import (
    AIProviderException,
)
from MatchCV.AI.Models.AIAnalysisResponse import (
    AIAnalysisResponse,
)
from MatchCV.AI.Services.IAIProvider import IAIProvider


class AIProviderService:
    """
    Coordena os provedores de IA e executa fallback
    quando uma falha elegível ocorre.
    """

    def __init__(
        self,
        primary_provider: IAIProvider,
        fallback_provider: IAIProvider,
    ) -> None:
        self._primary_provider = primary_provider
        self._fallback_provider = fallback_provider

    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> AIAnalysisResponse:
        try:
            return self._primary_provider.analyze(
                resume_text=resume_text,
                job_description=job_description,
            )
        except AIProviderException as exception:
            if not exception.retryable:
                raise

        return self._fallback_provider.analyze(
            resume_text=resume_text,
            job_description=job_description,
        )
