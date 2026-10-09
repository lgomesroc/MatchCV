
import os
from dataclasses import replace

import pytest

from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection


def create_test_settings(**overrides) -> AppSettings:
    values = {
        "environment": "test",
        "database_host": "sql-test",
        "database_port": 1433,
        "database_name": "MatchCV_Test",
        "database_user": "test_user",
        "database_password": "test_password",
        "ai_primary_api_key": "",
        "ai_primary_model": "",
        "ai_primary_base_url": "",
        "ai_primary_timeout_seconds": 1,
        "ai_fallback_api_key": "",
        "ai_fallback_model": "",
        "ai_fallback_base_url": "",
        "ai_fallback_timeout_seconds": 1,
    }

    values.update(overrides)
    return AppSettings(**values)


class TestDatabaseConnectionConfiguration:
    def test_builds_connection_string_with_expected_settings(self):
        settings = create_test_settings()
        database = DatabaseConnection(settings=settings)

        connection_string = database._build_connection_string()

        assert "DRIVER={ODBC Driver 18 for SQL Server};" in connection_string
        assert "SERVER=sql-test,1433;" in connection_string
        assert "DATABASE=MatchCV_Test;" in connection_string
        assert "UID=test_user;" in connection_string
        assert "PWD=test_password;" in connection_string
        assert "Encrypt=no;" in connection_string
        assert "TrustServerCertificate=yes;" in connection_string

    @pytest.mark.parametrize(
        ("field_name", "expected_message"),
        [
            ("database_host", "database_host"),
            ("database_name", "database_name"),
            ("database_user", "database_user"),
            ("database_password", "database_password"),
        ],
    )
    def test_rejects_missing_required_settings(
        self,
        field_name: str,
        expected_message: str,
    ):
        settings = create_test_settings(
            **{field_name: ""}
        )
        database = DatabaseConnection(settings=settings)

        with pytest.raises(RuntimeError, match=expected_message):
            database._build_connection_string()


class TestDatabaseConnectionIntegration:
    def test_connects_to_the_configured_database(
        self,
        integration_database_connection: DatabaseConnection,
    ):
        with integration_database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute("SELECT DB_NAME()")
                row = cursor.fetchone()
            finally:
                cursor.close()

        assert row is not None
        assert row[0] == os.environ["MATCHCV_TEST_DATABASE_NAME"]
