import json

from MatchCV.AI.Exceptions.AIProviderException import (
    AIProviderException,
)
from MatchCV.AI.Models.AIAnalysisResponse import (
    AIAnalysisResponse,
)


class AIResponseParser:
    """Valida e converte a resposta JSON do provedor."""

    REQUIRED_FIELDS = {
        "evidenced_requirements",
        "unevidenced_requirements",
        "gaps",
        "resume_issues",
        "suggestions",
    }

    @classmethod
    def parse(
        cls,
        raw_response: str,
    ) -> AIAnalysisResponse:
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as exception:
            raise AIProviderException(
                "O provedor retornou uma resposta JSON inválida.",
                retryable=False,
            ) from exception

        if not isinstance(data, dict):
            raise AIProviderException(
                "A resposta do provedor possui formato inválido.",
                retryable=False,
            )

        missing_fields = cls.REQUIRED_FIELDS - data.keys()

        if missing_fields:
            raise AIProviderException(
                "A resposta do provedor não possui todos os "
                "campos obrigatórios.",
                retryable=False,
            )

        for field_name in cls.REQUIRED_FIELDS:
            value = data[field_name]

            if not isinstance(value, list):
                raise AIProviderException(
                    f"O campo '{field_name}' deve ser uma lista.",
                    retryable=False,
                )

            if not all(
                isinstance(item, str)
                for item in value
            ):
                raise AIProviderException(
                    f"O campo '{field_name}' deve conter somente textos.",
                    retryable=False,
                )

        return AIAnalysisResponse(
            evidenced_requirements=data["evidenced_requirements"],
            unevidenced_requirements=data["unevidenced_requirements"],
            gaps=data["gaps"],
            resume_issues=data["resume_issues"],
            suggestions=data["suggestions"],
        )
