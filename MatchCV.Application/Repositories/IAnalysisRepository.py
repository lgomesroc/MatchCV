from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from MatchCV.Domain.Entities.Analysis import Analysis


class IAnalysisRepository(ABC):
    """Contrato de persistência de análises."""

    @abstractmethod
    def add(
        self,
        analysis: Analysis,
    ) -> Analysis:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        analysis_id: UUID,
    ) -> Optional[Analysis]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        analysis: Analysis,
    ) -> Analysis:
        raise NotImplementedError
