from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from MatchCV.Application.Queue.AnalysisQueueItem import (
    AnalysisQueueItem,
)


class IAnalysisQueueRepository(ABC):
    """Contrato para persistência da fila de análises."""

    @abstractmethod
    def enqueue(
        self,
        analysis_id: UUID,
        payload_ciphertext: bytes,
    ) -> AnalysisQueueItem:
        raise NotImplementedError

    @abstractmethod
    def get_next_pending(self) -> Optional[AnalysisQueueItem]:
        raise NotImplementedError

    @abstractmethod
    def mark_processing(
        self,
        queue_id: UUID,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_completed(
        self,
        queue_id: UUID,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_failed(
        self,
        queue_id: UUID,
        error: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def recover_processing(self) -> int:
        raise NotImplementedError
