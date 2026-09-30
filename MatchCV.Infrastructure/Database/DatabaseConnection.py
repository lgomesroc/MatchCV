from contextlib import contextmanager
from typing import Generator

from MatchCV.Infrastructure.Config.AppSettings import AppSettings


class DatabaseConnection:
    """Gerencia conexões com o banco de dados."""

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:
        self._settings = settings

    @contextmanager
    def connection(self) -> Generator[object, None, None]:
        """
        Abre uma conexão com o banco.

        A implementação concreta do driver será adicionada
        na camada de infraestrutura.
        """
        connection = None

        try:
            yield connection
        finally:
            if connection is not None:
                connection.close()
