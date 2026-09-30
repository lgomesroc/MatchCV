from MatchCV.AI.Models.AIAnalysisResponse import (
    AIAnalysisResponse,
)
from MatchCV.AI.Models.AIProviderConfig import AIProviderConfig
from MatchCV.AI.Services.AIHttpClient import AIHttpClient
from MatchCV.AI.Services.AIResponseParser import AIResponseParser
from MatchCV.AI.Services.AnalysisPromptBuilder import (
    AnalysisPromptBuilder,
)
from MatchCV.AI.Services.IAIProvider import IAIProvider


class SecondaryAIProvider(IAIProvider):
    """Segundo provedor utilizado como fallback."""

    def __init__(
        self,
        config: AIProviderConfig,
    ) -> None:
        self._config = config

    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> AIAnalysisResponse:
        payload = {
            "model": self._config.model,
            "messages": [
                {
                    "role": "system",
                    "content": AnalysisPromptBuilder.SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        f"DESCRIÇÃO DA VAGA:\n"
                        f"{job_description}\n\n"
                        f"CURRÍCULO:\n"
                        f"{resume_text}\n\n"
                        f"FORMATO DE RESPOSTA:\n"
                        f"{AnalysisPromptBuilder.OUTPUT_FORMAT}"
                    ),
                },
            ],
            "temperature": 0,
        }

        response = AIHttpClient.post_json(
            url=self._config.base_url,
            headers={
                "Authorization": (
                    f"Bearer {self._config.api_key}"
                ),
            },
            payload=payload,
            timeout_seconds=self._config.timeout_seconds,
        )

        content = response["choices"][0]["message"]["content"]

        return AIResponseParser.parse(content)
