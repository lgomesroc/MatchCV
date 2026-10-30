from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection


class SqlServerPasswordResetRepository:
    def __init__(self, database_connection: DatabaseConnection) -> None:
        self._database_connection = database_connection

    def create_token(self, email: str, token_hash: str) -> bool:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT id FROM dbo.users WHERE email = ? AND role = 'USER'",
                    email.strip().lower(),
                )
                row = cursor.fetchone()
                if row is None:
                    connection.rollback()
                    return False

                user_id = str(row[0])
                cursor.execute(
                    "UPDATE dbo.password_reset_tokens "
                    "SET used_at = SYSUTCDATETIME() "
                    "WHERE user_id = ? AND used_at IS NULL",
                    user_id,
                )
                cursor.execute(
                    "INSERT INTO dbo.password_reset_tokens "
                    "(token_hash, user_id, created_at, expires_at, used_at) "
                    "VALUES (?, ?, SYSUTCDATETIME(), "
                    "DATEADD(MINUTE, 15, SYSUTCDATETIME()), NULL)",
                    token_hash,
                    user_id,
                )
                connection.commit()
                return True
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    def revoke_token(self, token_hash: str) -> None:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE dbo.password_reset_tokens "
                    "SET used_at = SYSUTCDATETIME() "
                    "WHERE token_hash = ? AND used_at IS NULL",
                    token_hash,
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    def consume_token(self, token_hash: str, password_hash: str) -> bool:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE dbo.password_reset_tokens "
                    "SET used_at = SYSUTCDATETIME() "
                    "OUTPUT inserted.user_id "
                    "WHERE token_hash = ? AND used_at IS NULL "
                    "AND expires_at > SYSUTCDATETIME()",
                    token_hash,
                )
                row = cursor.fetchone()
                if row is None:
                    connection.rollback()
                    return False

                cursor.execute(
                    "UPDATE dbo.users SET password_hash = ? "
                    "WHERE id = ? AND role = 'USER'",
                    password_hash,
                    str(row[0]),
                )
                if cursor.rowcount != 1:
                    connection.rollback()
                    return False
                connection.commit()
                return True
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
