
import os

import pytest

from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)


@pytest.fixture(scope="session")
def test_database_settings() -> AppSettings:
    required_variables = (
        "MATCHCV_TEST_DATABASE_NAME",
        "MATCHCV_TEST_DATABASE_HOST",
        "MATCHCV_TEST_DATABASE_USER",
        "MATCHCV_TEST_DATABASE_PASSWORD",
    )

    missing_variables = [
        name
        for name in required_variables
        if not os.getenv(name)
    ]

    if missing_variables:
        pytest.skip(
            "Testes de integração com banco ignorados: configure "
            "as variáveis MATCHCV_TEST_DATABASE_*."
        )

    database_name = os.environ[
        "MATCHCV_TEST_DATABASE_NAME"
    ].strip()

    if database_name.casefold() == "matchcv":
        pytest.fail(
            "Por segurança, os testes de integração não podem "
            "utilizar o banco MatchCV de desenvolvimento."
        )

    return AppSettings(
        environment="test",
        database_host=os.environ[
            "MATCHCV_TEST_DATABASE_HOST"
        ],
        database_port=int(
            os.getenv("MATCHCV_TEST_DATABASE_PORT", "1433")
        ),
        database_name=database_name,
        database_user=os.environ[
            "MATCHCV_TEST_DATABASE_USER"
        ],
        database_password=os.environ[
            "MATCHCV_TEST_DATABASE_PASSWORD"
        ],
        ai_primary_api_key="",
        ai_primary_model="",
        ai_primary_base_url="",
        ai_primary_timeout_seconds=1,
        ai_fallback_api_key="",
        ai_fallback_model="",
        ai_fallback_base_url="",
        ai_fallback_timeout_seconds=1,
    )


@pytest.fixture(scope="session")
def test_database_connection(
    test_database_settings: AppSettings,
) -> DatabaseConnection:
    return DatabaseConnection(
        settings=test_database_settings,
    )


@pytest.fixture(scope="session")
def integration_database_connection(
    test_database_connection: DatabaseConnection,
) -> DatabaseConnection:
    return test_database_connection


@pytest.fixture
def cleanup_registry(
    test_database_connection: DatabaseConnection,
):
    registry = {
        "analysis_ids": [],
        "job_description_ids": [],
        "user_ids": [],
    }

    yield registry

    with test_database_connection.connection() as connection:
        cursor = connection.cursor()

        try:
            for analysis_id in registry["analysis_ids"]:
                cursor.execute(
                    "DELETE FROM dbo.analyses WHERE id = ?",
                    str(analysis_id),
                )

            for job_description_id in registry[
                "job_description_ids"
            ]:
                cursor.execute(
                    """
                    DELETE FROM dbo.job_descriptions
                    WHERE id = ?
                    """,
                    str(job_description_id),
                )

            for user_id in registry["user_ids"]:
                cursor.execute(
                    "DELETE FROM dbo.users WHERE id = ?",
                    str(user_id),
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
