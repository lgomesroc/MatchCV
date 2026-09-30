from dataclasses import dataclass
from uuid import UUID, uuid4

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Parser.Validation.ProfanityValidator import (
    ProfanityValidator,
)


@dataclass
class Resume:
    id: UUID
    file_name: str
    file_type: FileType
    file_size_bytes: int
    page_count: int
    extracted_text: str

    MAX_FILE_SIZE_BYTES = 1_048_576
    MAX_PAGE_COUNT = 2
    MIN_USEFUL_CHARACTERS = 30

    @classmethod
    def create(
        cls,
        file_name: str,
        file_type: FileType,
        file_size_bytes: int,
        page_count: int,
        extracted_text: str,
    ) -> "Resume":
        if not file_name or not file_name.strip():
            raise DomainException(
                "O nome do arquivo é obrigatório."
            )

        if file_size_bytes <= 0:
            raise DomainException(
                "O tamanho do arquivo deve ser maior que zero."
            )

        if file_size_bytes > cls.MAX_FILE_SIZE_BYTES:
            raise DomainException(
                "O currículo não pode ultrapassar 1 MB."
            )

        if page_count <= 0:
            raise DomainException(
                "O currículo deve possuir pelo menos uma página."
            )

        if page_count > cls.MAX_PAGE_COUNT:
            raise DomainException(
                "O currículo não pode possuir mais de duas páginas."
            )

        if not extracted_text or not extracted_text.strip():
            raise DomainException(
                "O currículo deve possuir texto extraível."
            )

        normalized_text = extracted_text.strip()

        useful_characters = len(
            "".join(
                character
                for character in normalized_text
                if character.isalnum()
            )
        )

        if useful_characters < cls.MIN_USEFUL_CHARACTERS:
            raise DomainException(
                "O currículo deve possuir pelo menos "
                "30 caracteres úteis."
            )

        try:
            ProfanityValidator.validate(
                normalized_text,
                "O currículo",
            )
        except Exception as exception:
            raise DomainException(str(exception)) from exception

        return cls(
            id=uuid4(),
            file_name=file_name.strip(),
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            page_count=page_count,
            extracted_text=normalized_text,
        )
