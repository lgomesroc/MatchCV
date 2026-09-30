from abc import ABC, abstractmethod
from typing import Any


class IAnalysisProvider(ABC):
    """Contrato para provedores de análise por IA."""

    @abstractmethod
    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> dict[str, Any]:
        """
        Analisa o currículo em relação à descrição da vaga.

        O provedor deve retornar uma estrutura de dados
        compatível com o resultado esperado pela aplicação.
        """
        raise NotImplementedError
