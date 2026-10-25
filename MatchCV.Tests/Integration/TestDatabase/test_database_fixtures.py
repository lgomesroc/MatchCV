import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection


load_dotenv(PROJECT_ROOT / ".env.test", override=True)


@pytest.fixture(scope="session")
def integration_database_connection() -> DatabaseConnection:
    host = os.getenv("MATCHCV_TEST_DATABASE_HOST", "127.0.0.1")
    port_value = os.getenv("MATCHCV_TEST_DATABASE_PORT", "1435")
    name = os.getenv("MATCHCV_TEST_DATABASE_NAME", "MatchCVTest")
    user = os.getenv("MATCHCV_TEST_DATABASE_USER", "sa")
    password = os.getenv("TEST_DATABASE_PASSWORD", "")

    if host not in {"127.0.0.1", "localhost"}:
        pytest.fail(
            "Por segurança, os testes só podem acessar o SQL Server local."
        )

    if name != "MatchCVTest":
        pytest.fail("O banco de testes deve ser MatchCVTest.")

    if user != "sa":
        pytest.fail("O usuário esperado para o banco de testes é sa.")

    try:
        port = int(port_value)
    except (TypeError, ValueError):
        pytest.fail("A porta do banco de testes deve ser numérica.")

    if port != 1435:
        pytest.fail("A porta do banco de testes deve ser 1435.")

    if not password:
        pytest.fail(
            "Defina TEST_DATABASE_PASSWORD no arquivo .env.test."
        )

    settings = AppSettings(
        environment="test",
        database_host=host,
        database_port=port,
        database_name=name,
        database_user=user,
        database_password=password,
        ai_primary_api_key="",
        ai_primary_model="",
        ai_primary_base_url="",
        ai_primary_timeout_seconds=1,
        ai_fallback_api_key="",
        ai_fallback_model="",
        ai_fallback_base_url="",
        ai_fallback_timeout_seconds=1,
        analysis_queue_encryption_key="",
    )

    return DatabaseConnection(settings=settings)


@pytest.fixture(scope="session")
def test_database_connection(
    integration_database_connection: DatabaseConnection,
) -> DatabaseConnection:
    return integration_database_connection


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

            for job_description_id in registry["job_description_ids"]:
                cursor.execute(
                    "DELETE FROM dbo.job_descriptions WHERE id = ?",
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
