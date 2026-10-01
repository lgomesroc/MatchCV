from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from MatchCV.Domain.Enums.UserRole import UserRole


@dataclass
class UserRecord:
    """Representação de um usuário persistido no banco."""

    id: UUID
    name: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime
