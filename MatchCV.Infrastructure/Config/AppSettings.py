from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppSettings:
    """Configurações gerais da aplicação."""

    environment: str
    database_url: str
    ai_primary_api_key: str
    ai_primary_model: str
    ai_primary_base_url: str
    ai_primary_timeout_seconds: int
    ai_fallback_api_key: str
    ai_fallback_model: str
    ai_fallback_base_url: str
    ai_fallback_timeout_seconds: int

    @classmethod
    def from_environment(cls) -> "AppSettings":
        return cls(
            environment=os.getenv(
                "APP_ENVIRONMENT",
                "development",
            ),
            database_url=os.getenv(
                "DATABASE_URL",
                "",
            ),
            ai_primary_api_key=os.getenv(
                "AI_PRIMARY_API_KEY",
                "",
            ),
            ai_primary_model=os.getenv(
                "AI_PRIMARY_MODEL",
                "",
            ),
            ai_primary_base_url=os.getenv(
                "AI_PRIMARY_BASE_URL",
                "",
            ),
            ai_primary_timeout_seconds=int(
                os.getenv(
                    "AI_PRIMARY_TIMEOUT_SECONDS",
                    "60",
                )
            ),
            ai_fallback_api_key=os.getenv(
                "AI_FALLBACK_API_KEY",
                "",
            ),
            ai_fallback_model=os.getenv(
                "AI_FALLBACK_MODEL",
                "",
            ),
            ai_fallback_base_url=os.getenv(
                "AI_FALLBACK_BASE_URL",
                "",
            ),
            ai_fallback_timeout_seconds=int(
                os.getenv(
                    "AI_FALLBACK_TIMEOUT_SECONDS",
                    "60",
                )
            ),
        )
