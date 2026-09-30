from dataclasses import dataclass
from uuid import UUID, uuid4

from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Parser.Validation.ProfanityValidator import (
    ProfanityValidator,
)
from MatchCV.Parser.Validation.TextContentValidator import (
    TextContentValidator,
)


@dataclass
class User:
    id: UUID
    name: str
    email: str
    password_hash: str
    role: UserRole

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
    ) -> "User":
        try:
            normalized_name = TextContentValidator.validate_name(
                name
            )
        except Exception as exception:
            raise DomainException(str(exception)) from exception

        try:
            ProfanityValidator.validate(
                normalized_name,
                "O nome",
            )
        except Exception as exception:
            raise DomainException(str(exception)) from exception

        if not email or not email.strip():
            raise DomainException(
                "O e-mail é obrigatório."
            )

        if email != email.strip():
            raise DomainException(
                "O e-mail não pode possuir espaços "
                "no início ou no final."
            )

        if not password_hash or not password_hash.strip():
            raise DomainException(
                "O hash da senha é obrigatório."
            )

        if not isinstance(role, UserRole):
            raise DomainException(
                "O papel do usuário é inválido."
            )

        return cls(
            id=uuid4(),
            name=normalized_name,
            email=email.strip(),
            password_hash=password_hash,
            role=role,
        )
