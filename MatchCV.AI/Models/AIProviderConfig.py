from dataclasses import dataclass


@dataclass(frozen=True)
class AIProviderConfig:
    """Configuração de um provedor de IA."""

    name: str
    api_key: str
    model: str
