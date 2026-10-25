from uuid import UUID, uuid4

from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)


class SqlServerAnalysisUsageRepository:
    """Registra análises concluídas associadas ao usuário autenticado."""

    FREE_ANALYSIS_LIMIT = 3

    def __init__(self, database_connection: DatabaseConnection) -> None:
        self._database_connection = database_connection

    def count_completed(self, user_id: UUID) -> int:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.analyses
                    WHERE user_id = ?
                      AND status = N'COMPLETED'
                      AND created_at >= DATEFROMPARTS(YEAR(SYSUTCDATETIME()), MONTH(SYSUTCDATETIME()), 1)
                      AND created_at < DATEADD(MONTH, 1, DATEFROMPARTS(YEAR(SYSUTCDATETIME()), MONTH(SYSUTCDATETIME()), 1))
                    """,
                    str(user_id),
                )
                row = cursor.fetchone()
                return int(row[0])
            finally:
                cursor.close()

    def record_success(self, user_id: UUID) -> None:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.user_analysis_usage (id, user_id)
                    VALUES (?, ?)
                    """,
                    str(uuid4()),
                    str(user_id),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
