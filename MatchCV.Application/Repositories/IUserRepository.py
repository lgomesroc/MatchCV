from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from MatchCV.Domain.Entities.User import User


class IUserRepository(ABC):
    """Contrato de persistência de usuários."""

    @abstractmethod
    def add(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        user_id: UUID,
    ) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def update_password_hash(self, user_id: UUID, password_hash: str) -> bool:
        """Atualiza o hash da senha; implementado pelo repositório concreto."""
        raise NotImplementedError

    def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        raise NotImplementedError
