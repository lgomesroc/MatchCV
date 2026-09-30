from dataclasses import dataclass
from typing import List


@dataclass
class AIAnalysisResponse:
    """Resposta estruturada produzida pelo provedor de IA."""

    evidenced_requirements: List[str]
    unevidenced_requirements: List[str]
    gaps: List[str]
    resume_issues: List[str]
    suggestions: List[str]
