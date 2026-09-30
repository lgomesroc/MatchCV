from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
