class AIProviderException(Exception):
    """Exceção para falhas relacionadas ao provedor de IA."""

    def __init__(
        self,
        message: str,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
