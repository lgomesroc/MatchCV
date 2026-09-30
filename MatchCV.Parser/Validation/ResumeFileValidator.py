from pathlib import Path

from MatchCV.Parser.Exceptions.ParserException import ParserException


class ResumeFileValidator:
    """Valida as características básicas do arquivo enviado."""

    MAX_FILE_SIZE_BYTES = 1_048_576

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
    }

    @classmethod
    def validate(
        cls,
        file_name: str,
        file_size_bytes: int,
    ) -> None:
        if not file_name or not file_name.strip():
            raise ParserException(
                "O nome do arquivo é obrigatório."
            )

        if file_size_bytes <= 0:
            raise ParserException(
                "O arquivo deve possuir tamanho maior que zero."
            )

        if file_size_bytes > cls.MAX_FILE_SIZE_BYTES:
            raise ParserException(
                "O currículo não pode ultrapassar 1 MB."
            )

        extension = Path(file_name).suffix.lower()

        if extension not in cls.ALLOWED_EXTENSIONS:
            raise ParserException(
                "Formato de currículo não suportado."
            )
