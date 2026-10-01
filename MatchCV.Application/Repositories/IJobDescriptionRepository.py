from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from MatchCV.Domain.Entities.JobDescription import JobDescription


class IJobDescriptionRepository(ABC):
    """Contrato de persistência de descrições de vagas."""

    @abstractmethod
    def add(
        self,
        job_description: JobDescription,
    ) -> JobDescription:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        job_description_id: UUID,
    ) -> Optional[JobDescription]:
        raise NotImplementedError
