from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class JobDescriptionRecord:
    """Representação de uma descrição de vaga persistida."""

    id: UUID
    content: str
    created_at: datetime
