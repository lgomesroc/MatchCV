
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus


@dataclass
class AnalysisRecord:
    """Representação de uma análise persistida."""

    id: UUID
    resume_id: UUID
    job_description_id: UUID
    status: AnalysisStatus
    evidenced_requirements: List[str]
    unevidenced_requirements: List[str]
    gaps: List[str]
    resume_issues: List[str]
    suggestions: List[str]
    created_at: datetime
    completed_at: Optional[datetime]
