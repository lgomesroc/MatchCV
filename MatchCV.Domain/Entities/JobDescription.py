from dataclasses import dataclass
from uuid import UUID, uuid4

from MatchCV.Domain.Exceptions.DomainException import DomainException


@dataclass
class JobDescription:
    id: UUID
    content: str

    @classmethod
    def create(cls, content: str) -> "JobDescription":
        if not content or not content.strip():
            raise DomainException(
                "A descrição da vaga é obrigatória."
            )

        normalized_content = content.strip()

        useful_characters = len(
            "".join(
                character
                for character in normalized_content
                if character.isalnum()
            )
        )

        if useful_characters < 30:
            raise DomainException(
                "A descrição da vaga deve possuir pelo menos 30 caracteres úteis."
            )

        if len(normalized_content) > 3000:
            raise DomainException(
                "A descrição da vaga não pode ultrapassar 3000 caracteres."
            )

        return cls(
            id=uuid4(),
            content=normalized_content,
        )
