from dataclasses import dataclass
from uuid import UUID, uuid4

from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Domain.Validation.ProfanityValidator import (
    ProfanityValidator,
)
from MatchCV.Domain.Validation.TextContentValidator import (
    TextContentValidator,
)


@dataclass
class JobDescription:
    id: UUID
    content: str

    MIN_USEFUL_CHARACTERS = 30
    MAX_CHARACTERS = 3000

    @classmethod
    def create(
        cls,
        content: str,
    ) -> "JobDescription":
        normalized_content = (
            TextContentValidator.validate_job_description(
                content
            )
        )

        useful_characters = len(
            "".join(
                character
                for character in normalized_content
                if character.isalnum()
            )
        )

        if useful_characters < cls.MIN_USEFUL_CHARACTERS:
            raise DomainException(
                "A descrição da vaga deve possuir pelo menos "
                "30 caracteres úteis."
            )

        if len(normalized_content) > cls.MAX_CHARACTERS:
            raise DomainException(
                "A descrição da vaga não pode ultrapassar "
                "3000 caracteres."
            )

        ProfanityValidator.validate(
            normalized_content,
            "A descrição da vaga",
        )

        return cls(
            id=uuid4(),
            content=normalized_content,
        )
