class DomainException(Exception):
    """Exceção para violações de regras de negócio do domínio."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
