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
        user_id: UUID,
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

    @abstractmethod
    def list_by_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id_and_user(
        self,
        analysis_id: UUID,
        user_id: UUID,
    ) -> Optional[Analysis]:
        raise NotImplementedError

    @abstractmethod
    def claim_pending(
        self,
        limit: int = 10,
    ) -> list[Analysis]:
        """
        Reserva análises pendentes para processamento pelo worker.

        A implementação deve garantir que a mesma análise não
        seja reservada simultaneamente por outro worker.
        """
        raise NotImplementedError
