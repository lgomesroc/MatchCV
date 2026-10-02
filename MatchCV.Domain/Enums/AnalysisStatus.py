from enum import Enum


class AnalysisStatus(str, Enum):
    """
    Estados possíveis de uma análise de currículo.
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
