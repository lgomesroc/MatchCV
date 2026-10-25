from uuid import UUID, uuid4

from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection


class SqlServerAnalysisUsageRepository:
    """Controla a cota mensal gratuita com reservas concorrentes seguras."""

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

    def reserve_monthly_slot(self, user_id: UUID) -> UUID:
        """Reserva atomicamente uma vaga do mês antes de enfileirar a análise."""
        reservation_id = uuid4()
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    DECLARE @lock_result INT;
                    EXEC @lock_result = sys.sp_getapplock
                        @Resource = ?,
                        @LockMode = N'Exclusive',
                        @LockOwner = N'Transaction',
                        @LockTimeout = 10000;
                    IF @lock_result < 0
                        THROW 51001, 'Não foi possível reservar a cota mensal.', 1;

                    DECLARE @month_start DATETIME2 =
                        DATEFROMPARTS(YEAR(SYSUTCDATETIME()), MONTH(SYSUTCDATETIME()), 1);

                    DECLARE @used INT;
                    SELECT @used = COUNT(*)
                    FROM dbo.analysis_quota_reservations WITH (UPDLOCK, HOLDLOCK)
                    WHERE user_id = ?
                      AND month_start = @month_start
                      AND status IN (N'RESERVED', N'COMPLETED');

                    IF @used >= ?
                        THROW 51002, 'Limite mensal de análises atingido.', 1;

                    INSERT INTO dbo.analysis_quota_reservations
                        (id, user_id, month_start, status)
                    VALUES (?, ?, @month_start, N'RESERVED');
                    """,
                    f"MatchCV:MonthlyQuota:{user_id}",
                    str(user_id),
                    self.FREE_ANALYSIS_LIMIT,
                    str(reservation_id),
                    str(user_id),
                )
                connection.commit()
                return reservation_id
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    def complete_reservation(self, reservation_id: UUID) -> None:
        self._update_reservation(reservation_id, "COMPLETED")

    def release_reservation(self, reservation_id: UUID) -> None:
        self._update_reservation(reservation_id, "RELEASED")

    def _update_reservation(self, reservation_id: UUID, status: str) -> None:
        if status not in {"COMPLETED", "RELEASED"}:
            raise ValueError("Status de reserva inválido.")
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_quota_reservations
                    SET status = ?
                    WHERE id = ? AND status = N'RESERVED'
                    """,
                    status,
                    str(reservation_id),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
