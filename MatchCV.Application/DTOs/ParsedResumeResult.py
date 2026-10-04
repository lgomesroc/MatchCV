from dataclasses import dataclass

from MatchCV.Domain.Enums.FileType import FileType


@dataclass
class ParsedResumeResult:
    """
    Resultado do processamento do currículo exposto para a camada
    Application.

    Não depende de classes da camada Parser.
    """

    file_name: str
    file_type: FileType
    file_size_bytes: int
    page_count: int
    extracted_text: str
    is_text_extractable: bool
    is_single_column: bool
    has_images: bool
    is_password_protected: bool
