def test_connects_to_the_test_database(integration_database_connection):
    with integration_database_connection.connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DB_NAME()")
            row = cursor.fetchone()
        finally:
            cursor.close()

    assert row is not None
    assert row[0] == "MatchCVTest"
