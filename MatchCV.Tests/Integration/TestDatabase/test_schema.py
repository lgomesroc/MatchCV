def test_required_tables_exist(integration_database_connection):
    expected_tables = {
        "users",
        "job_descriptions",
        "analyses",
        "analysis_queue",
        "analysis_quota_reservations",
        "user_analysis_usage",
        "password_reset_tokens",
        "admin_password_policy",
    }

    with integration_database_connection.connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'dbo'
                  AND TABLE_TYPE = 'BASE TABLE'
            """)
            actual_tables = {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()

    missing = expected_tables - actual_tables
    assert not missing, f"Tabelas ausentes: {sorted(missing)}"


def test_expected_indexes_exist(integration_database_connection):
    expected_indexes = {
        "IX_analysis_queue_pending",
        "IX_analysis_quota_reservations_month_user_status",
        "UX_analysis_quota_reservations_analysis",
        "UX_users_single_admin",
    }

    with integration_database_connection.connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT name
                FROM sys.indexes
                WHERE object_id IN (
                    SELECT object_id
                    FROM sys.tables
                    WHERE schema_id = SCHEMA_ID('dbo')
                )
            """)
            actual_indexes = {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()

    missing = expected_indexes - actual_indexes
    assert not missing, f"Índices ausentes: {sorted(missing)}"
