from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class AnalyzeResumeRequest:
    """Dados necessários para solicitar uma análise."""

    file_stream: BinaryIO
    file_name: str
    file_size_bytes: int
    job_description: str
