import re

from MatchCV.Domain.Exceptions.DomainException import DomainException


class TextContentValidator:
    """Valida regras estruturais comuns para conteúdos textuais."""

    @staticmethod
    def normalize_whitespace(
        value: str,
    ) -> str:
        """Normaliza sequências de whitespace para um único espaço."""
        return re.sub(r"\s+", " ", value)

    @staticmethod
    def validate_required(
        value: str | None,
        field_name: str,
    ) -> str:
        if value is None:
            raise DomainException(
                f"{field_name} é obrigatório."
            )

        if not value:
            raise DomainException(
                f"{field_name} não pode ser vazio."
            )

        if not value.strip():
            raise DomainException(
                f"{field_name} não pode conter somente espaços."
            )

        normalized_value = (
            TextContentValidator.normalize_whitespace(
                value
            ).strip()
        )

        if not normalized_value:
            raise DomainException(
                f"{field_name} não pode conter somente espaços."
            )

        return normalized_value

    @staticmethod
    def validate_not_only_numbers(
        value: str,
        field_name: str,
    ) -> None:
        characters = [
            character
            for character in value
            if not character.isspace()
        ]

        if characters and all(
            character.isdigit()
            for character in characters
        ):
            raise DomainException(
                f"{field_name} não pode conter somente números."
            )

    @staticmethod
    def validate_not_only_special_characters(
        value: str,
        field_name: str,
    ) -> None:
        characters = [
            character
            for character in value
            if not character.isspace()
        ]

        if characters and all(
            not character.isalnum()
            for character in characters
        ):
            raise DomainException(
                f"{field_name} não pode conter somente "
                "caracteres especiais."
            )

    @staticmethod
    def validate_first_character(
        value: str,
        field_name: str,
        allow_dot: bool = False,
    ) -> None:
        if not value:
            return

        first_character = value[0]

        if first_character.isalnum():
            return

        if allow_dot and first_character == ".":
            return

        raise DomainException(
            f"{field_name} não pode começar com "
            "caractere especial."
        )

    @staticmethod
    def validate_no_consecutive_special_characters(
        value: str,
        field_name: str,
    ) -> None:
        for current, following in zip(
            value,
            value[1:],
        ):
            current_is_special = (
                not current.isalnum()
                and not current.isspace()
            )

            following_is_special = (
                not following.isalnum()
                and not following.isspace()
            )

            if current_is_special and following_is_special:
                raise DomainException(
                    f"{field_name} não pode possuir "
                    "caracteres especiais consecutivos."
                )

    @staticmethod
    def validate_name(
        value: str | None,
    ) -> str:
        field_name = "O nome"

        normalized_value = (
            TextContentValidator.validate_required(
                value,
                field_name,
            )
        )

        TextContentValidator.validate_not_only_numbers(
            normalized_value,
            field_name,
        )

        TextContentValidator.validate_not_only_special_characters(
            normalized_value,
            field_name,
        )

        TextContentValidator.validate_first_character(
            normalized_value,
            field_name,
            allow_dot=False,
        )

        TextContentValidator.validate_no_consecutive_special_characters(
            normalized_value,
            field_name,
        )

        return normalized_value

    @staticmethod
    def validate_job_description(
        value: str | None,
    ) -> str:
        field_name = "A descrição da vaga"

        normalized_value = (
            TextContentValidator.validate_required(
                value,
                field_name,
            )
        )

        TextContentValidator.validate_not_only_numbers(
            normalized_value,
            field_name,
        )

        TextContentValidator.validate_not_only_special_characters(
            normalized_value,
            field_name,
        )

        TextContentValidator.validate_first_character(
            normalized_value,
            field_name,
            allow_dot=True,
        )

        return normalized_value
