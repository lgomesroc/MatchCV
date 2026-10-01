from contextlib import contextmanager
from typing import Generator

import psycopg

from MatchCV.Infrastructure.Config.AppSettings import AppSettings


class DatabaseConnection:
    """Gerencia conexões com o PostgreSQL."""

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:
        self._settings = settings

    @contextmanager
    def connection(self) -> Generator[psycopg.Connection, None, None]:
        """
        Abre uma conexão com o PostgreSQL e garante seu fechamento.
        """

        if not self._settings.database_url:
            raise RuntimeError(
                "DATABASE_URL não foi configurada."
            )

        connection = psycopg.connect(
            self._settings.database_url
        )

        try:
            yield connection
        finally:
            connection.close()
