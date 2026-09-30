from dataclasses import dataclass
from typing import Optional

from MatchCV.Domain.Enums.FileType import FileType


@dataclass
class ParsedResume:
    file_name: str
    file_type: FileType
    file_size_bytes: int
    page_count: int
    extracted_text: str
    is_text_extractable: bool
    is_single_column: Optional[bool]
    has_images: bool
    is_password_protected: bool
