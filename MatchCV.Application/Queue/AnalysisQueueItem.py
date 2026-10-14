from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AnalysisQueueItem:
    id: UUID
    analysis_id: UUID
    payload_ciphertext: bytes
    status: str
    attempts: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    last_error: str | None
