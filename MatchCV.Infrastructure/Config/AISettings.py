from MatchCV.AI.Models.AIProviderConfig import AIProviderConfig
from MatchCV.Infrastructure.Config.AppSettings import AppSettings


class AISettings:
    """Converte configurações da aplicação em configurações de IA."""

    @staticmethod
    def primary(
        settings: AppSettings,
    ) -> AIProviderConfig:
        return AIProviderConfig(
            name="primary",
            api_key=settings.ai_primary_api_key,
            model=settings.ai_primary_model,
            base_url=settings.ai_primary_base_url,
            timeout_seconds=settings.ai_primary_timeout_seconds,
        )

    @staticmethod
    def fallback(
        settings: AppSettings,
    ) -> AIProviderConfig:
        return AIProviderConfig(
            name="fallback",
            api_key=settings.ai_fallback_api_key,
            model=settings.ai_fallback_model,
            base_url=settings.ai_fallback_base_url,
            timeout_seconds=settings.ai_fallback_timeout_seconds,
        )
