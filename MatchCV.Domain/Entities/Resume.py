from dataclasses import dataclass
from uuid import UUID, uuid4

from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Domain.Exceptions.DomainException import DomainException


@dataclass
class Resume:
    id: UUID
    file_name: str
    file_type: FileType
    file_size_bytes: int
    page_count: int
    extracted_text: str

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
            raise DomainException("O nome do arquivo é obrigatório.")

        if file_size_bytes <= 0:
            raise DomainException("O tamanho do arquivo deve ser maior que zero.")

        if file_size_bytes > 1_048_576:
            raise DomainException("O currículo não pode ultrapassar 1 MB.")

        if page_count <= 0:
            raise DomainException("O currículo deve possuir pelo menos uma página.")

        if page_count > 2:
            raise DomainException(
                "O currículo não pode possuir mais de duas páginas."
            )

        if not extracted_text or not extracted_text.strip():
            raise DomainException(
                "O currículo deve possuir texto extraível."
            )

        useful_characters = len(
            "".join(character for character in extracted_text if character.isalnum())
        )

        if useful_characters < 30:
            raise DomainException(
                "O currículo deve possuir pelo menos 30 caracteres úteis."
            )

        return cls(
            id=uuid4(),
            file_name=file_name.strip(),
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            page_count=page_count,
            extracted_text=extracted_text.strip(),
        )
