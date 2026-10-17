from cryptography.fernet import Fernet


class AnalysisPayloadEncryption:
    """Criptografa e descriptografa dados temporários da fila."""

    def __init__(
        self,
        encryption_key: str,
    ) -> None:
        if not encryption_key:
            raise RuntimeError(
                "ANALYSIS_QUEUE_ENCRYPTION_KEY não foi configurada."
            )

        try:
            self._fernet = Fernet(
                encryption_key.encode("utf-8")
            )
        except Exception as exception:
            raise RuntimeError(
                "ANALYSIS_QUEUE_ENCRYPTION_KEY é inválida."
            ) from exception

    def encrypt(
        self,
        value: str,
    ) -> bytes:
        return self._fernet.encrypt(
            value.encode("utf-8")
        )

    def decrypt(
        self,
        value: bytes,
    ) -> str:
        return self._fernet.decrypt(value).decode("utf-8")
