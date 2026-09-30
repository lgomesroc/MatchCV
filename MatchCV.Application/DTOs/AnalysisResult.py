from dataclasses import dataclass
from typing import List


@dataclass
class AnalysisResult:
    """Resultado da análise de currículo."""

    evidenced_requirements: List[str]
    unevidenced_requirements: List[str]
    gaps: List[str]
    resume_issues: List[str]
    suggestions: List[str]
