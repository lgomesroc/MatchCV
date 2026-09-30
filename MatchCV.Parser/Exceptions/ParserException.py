class ParserException(Exception):
    """Exceção para erros durante o processamento de documentos."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
