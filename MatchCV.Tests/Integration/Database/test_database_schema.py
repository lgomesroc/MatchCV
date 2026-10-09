
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection


class TestDatabaseSchema:
    def test_required_tables_exist(
        self,
        integration_database_connection: DatabaseConnection,
    ):
        expected_tables = {
            "users",
            "job_descriptions",
            "analyses",
        }

        with integration_database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = ?
                      AND TABLE_TYPE = ?
                    """,
                    "dbo",
                    "BASE TABLE",
                )

                existing_tables = {
                    row[0] for row in cursor.fetchall()
                }
            finally:
                cursor.close()

        assert expected_tables.issubset(existing_tables)

    def test_users_table_has_required_columns(
        self,
        integration_database_connection: DatabaseConnection,
    ):
        expected_columns = {
            "id",
            "name",
            "email",
            "password_hash",
            "role",
            "created_at",
        }

        actual_columns = self._get_columns(
            integration_database_connection,
            "users",
        )

        assert expected_columns.issubset(actual_columns)

    def test_job_descriptions_table_has_required_columns(
        self,
        integration_database_connection: DatabaseConnection,
    ):
        expected_columns = {
            "id",
            "content",
            "created_at",
        }

        actual_columns = self._get_columns(
            integration_database_connection,
            "job_descriptions",
        )

        assert expected_columns.issubset(actual_columns)

    def test_analyses_table_has_required_columns(
        self,
        integration_database_connection: DatabaseConnection,
    ):
        expected_columns = {
            "id",
            "resume_id",
            "job_description_id",
            "status",
            "evidenced_requirements",
            "unevidenced_requirements",
            "gaps",
            "resume_issues",
            "suggestions",
            "created_at",
            "completed_at",
        }

        actual_columns = self._get_columns(
            integration_database_connection,
            "analyses",
        )

        assert expected_columns.issubset(actual_columns)

    @staticmethod
    def _get_columns(
        database_connection: DatabaseConnection,
        table_name: str,
    ) -> set[str]:
        with database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ?
                      AND TABLE_NAME = ?
                    """,
                    "dbo",
                    table_name,
                )

                return {
                    row[0] for row in cursor.fetchall()
                }
            finally:
                cursor.close()
