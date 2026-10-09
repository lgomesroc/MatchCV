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
        if content is None:
            raise DomainException(
                "A descrição da vaga é obrigatória."
            )

        if not content:
            raise DomainException(
                "A descrição da vaga não pode ser vazia."
            )

        if not content.strip():
            raise DomainException(
                "A descrição da vaga não pode conter somente espaços."
            )

        preserved_content = content.strip()

        TextContentValidator.validate_not_only_numbers(
            preserved_content,
            "A descrição da vaga",
        )

        TextContentValidator.validate_not_only_special_characters(
            preserved_content,
            "A descrição da vaga",
        )

        TextContentValidator.validate_first_character(
            preserved_content,
            "A descrição da vaga",
            allow_dot=True,
        )

        TextContentValidator.validate_no_emoji_or_emoticon(
            preserved_content,
            "A descrição da vaga",
        )

        useful_characters = len(
            "".join(
                character
                for character in preserved_content
                if character.isalnum()
            )
        )

        if useful_characters < cls.MIN_USEFUL_CHARACTERS:
            raise DomainException(
                "A descrição da vaga deve possuir pelo menos "
                "30 caracteres úteis."
            )

        if len(preserved_content) > cls.MAX_CHARACTERS:
            raise DomainException(
                "A descrição da vaga não pode ultrapassar "
                "3000 caracteres."
            )

        ProfanityValidator.validate(
            preserved_content,
            "A descrição da vaga",
        )

        return cls(
            id=uuid4(),
            content=preserved_content,
        )
