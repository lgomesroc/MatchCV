from MatchCV.AI.Exceptions.AIProviderException import (
    AIProviderException,
)
from MatchCV.AI.Models.AIAnalysisResponse import (
    AIAnalysisResponse,
)
from MatchCV.AI.Services.IAIProvider import IAIProvider


class AIProviderService:
    """
    Coordena o provedor principal e o provedor de fallback.

    Uma análise continua sendo uma única consulta mesmo quando
    ocorre fallback entre os provedores.
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

        except AIProviderException as primary_exception:
            print(
                "\n========== ERRO DO PROVEDOR PRINCIPAL =========="
            )
            print(str(primary_exception))
            print(
                f"retryable={primary_exception.retryable}"
            )
            print(
                "================================================\n"
            )

            if not primary_exception.retryable:
                raise

            try:
                return self._fallback_provider.analyze(
                    resume_text=resume_text,
                    job_description=job_description,
                )

            except AIProviderException as fallback_exception:
                raise AIProviderException(
                    "O provedor principal falhou e o provedor "
                    "de fallback também falhou. "
                    f"Erro do provedor principal: "
                    f"{primary_exception}. "
                    f"Erro do fallback: {fallback_exception}.",
                    retryable=False,
                ) from fallback_exception
