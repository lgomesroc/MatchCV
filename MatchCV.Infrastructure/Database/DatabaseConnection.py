from contextlib import contextmanager
from typing import Generator

import pyodbc

from MatchCV.Infrastructure.Config.AppSettings import AppSettings


class DatabaseConnection:
    """Gerencia conexões com o SQL Server."""

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:
        self._settings = settings

    @contextmanager
    def connection(self) -> Generator[pyodbc.Connection, None, None]:
        connection_string = self._build_connection_string()

        connection = pyodbc.connect(
            connection_string,
            autocommit=False,
        )

        try:
            yield connection
        finally:
            connection.close()

    def _build_connection_string(self) -> str:
        if not self._settings.database_host:
            raise RuntimeError(
                "DATABASE_HOST não foi configurada."
            )

        if not self._settings.database_name:
            raise RuntimeError(
                "DATABASE_NAME não foi configurada."
            )

        if not self._settings.database_user:
            raise RuntimeError(
                "DATABASE_USER não foi configurada."
            )

        if not self._settings.database_password:
            raise RuntimeError(
                "DATABASE_PASSWORD não foi configurada."
            )

        return (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self._settings.database_host},"
            f"{self._settings.database_port};"
            f"DATABASE={self._settings.database_name};"
            f"UID={self._settings.database_user};"
            f"PWD={self._settings.database_password};"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
