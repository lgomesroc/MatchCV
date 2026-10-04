from MatchCV.AI.Models.AIAnalysisResponse import (
    AIAnalysisResponse,
)
from MatchCV.AI.Services.IAIProvider import IAIProvider


class DevelopmentAIProvider(IAIProvider):
    """
    Provider local utilizado durante o desenvolvimento.

    Não realiza chamadas externas.
    Serve para validar o fluxo completo da aplicação
    antes da configuração dos provedores reais de IA.
    """

    def analyze(
        self,
        resume_text: str,
        job_description: str,
    ) -> AIAnalysisResponse:
        return AIAnalysisResponse(
            evidenced_requirements=[
                "Currículo recebido e processado com sucesso.",
                "Descrição da vaga recebida e processada com sucesso.",
            ],
            unevidenced_requirements=[
                "Análise real de requisitos ainda não executada por um provedor de IA.",
            ],
            gaps=[
                "O provider de desenvolvimento não realiza comparação semântica entre currículo e vaga.",
            ],
            resume_issues=[],
            suggestions=[
                "Configurar um provedor de IA real para realizar a análise semântica.",
            ],
        )
