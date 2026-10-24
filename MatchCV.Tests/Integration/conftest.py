
import os

import pytest

from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)


def _environment_value(
    test_variable: str,
    fallback_variable: str | None = None,
    default: str | None = None,
) -> str | None:
    value = os.getenv(test_variable)

    if value is not None and value.strip():
        return value.strip()

    if fallback_variable:
        value = os.getenv(fallback_variable)

        if value is not None and value.strip():
            return value.strip()

    return default


@pytest.fixture(scope="session")
def test_database_settings() -> AppSettings:
    database_name = _environment_value(
        "MATCHCV_TEST_DATABASE_NAME",
        default="MatchCV_Test",
    )
    database_host = _environment_value(
        "MATCHCV_TEST_DATABASE_HOST",
        "DATABASE_HOST",
    )
    database_port_value = _environment_value(
        "MATCHCV_TEST_DATABASE_PORT",
        "DATABASE_PORT",
        "1433",
    )
    database_user = _environment_value(
        "MATCHCV_TEST_DATABASE_USER",
        "DATABASE_USER",
    )
    database_password = _environment_value(
        "MATCHCV_TEST_DATABASE_PASSWORD",
        "DATABASE_PASSWORD",
    )

    missing_variables = []

    if not database_host:
        missing_variables.append(
            "MATCHCV_TEST_DATABASE_HOST ou DATABASE_HOST"
        )

    if not database_user:
        missing_variables.append(
            "MATCHCV_TEST_DATABASE_USER ou DATABASE_USER"
        )

    if not database_password:
        missing_variables.append(
            "MATCHCV_TEST_DATABASE_PASSWORD ou DATABASE_PASSWORD"
        )

    if missing_variables:
        pytest.fail(
            "Configuração do SQL Server de testes incompleta. "
            "Defina: "
            + ", ".join(missing_variables)
            + "."
        )

    if not database_name:
        pytest.fail(
            "O nome do banco de testes não foi configurado."
        )

    if database_name.casefold() == "matchcv":
        pytest.fail(
            "Por segurança, os testes de integração não podem "
            "utilizar o banco MatchCV de desenvolvimento. "
            "Configure MATCHCV_TEST_DATABASE_NAME=MatchCV_Test."
        )

    try:
        database_port = int(database_port_value)
    except (TypeError, ValueError):
        pytest.fail(
            "A porta do SQL Server de testes precisa ser um inteiro."
        )

    if not 1 <= database_port <= 65535:
        pytest.fail(
            "A porta do SQL Server de testes precisa estar "
            "entre 1 e 65535."
        )

    return AppSettings(
        environment="test",
        database_host=database_host,
        database_port=database_port,
        database_name=database_name,
        database_user=database_user,
        database_password=database_password,
        ai_primary_api_key="",
        ai_primary_model="",
        ai_primary_base_url="",
        ai_primary_timeout_seconds=1,
        ai_fallback_api_key="",
        ai_fallback_model="",
        ai_fallback_base_url="",
        ai_fallback_timeout_seconds=1,
        analysis_queue_encryption_key=os.getenv(
            "ANALYSIS_QUEUE_ENCRYPTION_KEY",
            "",
        ),
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
