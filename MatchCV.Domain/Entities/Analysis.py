from dataclasses import dataclass, field
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from MatchCV.Domain.Exceptions.DomainException import DomainException


class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Analysis:
    id: UUID
    resume_id: UUID
    job_description_id: UUID
    status: AnalysisStatus = AnalysisStatus.PENDING
    evidenced_requirements: List[str] = field(default_factory=list)
    unevidenced_requirements: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    resume_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        resume_id: UUID,
        job_description_id: UUID,
    ) -> "Analysis":
        if not resume_id:
            raise DomainException(
                "O currículo é obrigatório para criar uma análise."
            )

        if not job_description_id:
            raise DomainException(
                "A descrição da vaga é obrigatória para criar uma análise."
            )

        return cls(
            id=uuid4(),
            resume_id=resume_id,
            job_description_id=job_description_id,
        )

    def start_processing(self) -> None:
        if self.status != AnalysisStatus.PENDING:
            raise DomainException(
                "Somente análises pendentes podem iniciar o processamento."
            )

        self.status = AnalysisStatus.PROCESSING

    def complete(
        self,
        evidenced_requirements: List[str],
        unevidenced_requirements: List[str],
        gaps: List[str],
        resume_issues: List[str],
        suggestions: List[str],
    ) -> None:
        if self.status != AnalysisStatus.PROCESSING:
            raise DomainException(
                "Somente análises em processamento podem ser concluídas."
            )

        self.evidenced_requirements = evidenced_requirements
        self.unevidenced_requirements = unevidenced_requirements
        self.gaps = gaps
        self.resume_issues = resume_issues
        self.suggestions = suggestions
        self.status = AnalysisStatus.COMPLETED

    def fail(self) -> None:
        if self.status != AnalysisStatus.PROCESSING:
            raise DomainException(
                "Somente análises em processamento podem falhar."
            )

        self.status = AnalysisStatus.FAILED
