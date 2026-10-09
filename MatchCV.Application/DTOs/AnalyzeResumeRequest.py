from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class AnalyzeResumeRequest:
    """Dados necessários para solicitar uma análise."""

    job_description: str

    file_stream: BinaryIO | None = None
    file_name: str | None = None
    file_size_bytes: int | None = None

    resume_text: str | None = None
    