from uuid import UUID, uuid4

from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection


class MonthlyQuotaExceeded(Exception):
    """O usuário esgotou as vagas gratuitas do mês atual."""


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

                    DECLARE @reserved_or_completed INT;
                    DECLARE @legacy_completed INT;

                    SELECT @reserved_or_completed = COUNT(*)
                    FROM dbo.analysis_quota_reservations WITH (UPDLOCK, HOLDLOCK)
                    WHERE user_id = ?
                      AND month_start = CONVERT(DATE, @month_start)
                      AND status IN (N'RESERVED', N'COMPLETED');

                    SELECT @legacy_completed = COUNT(*)
                    FROM dbo.analyses AS a
                    WHERE a.user_id = ?
                      AND a.status = N'COMPLETED'
                      AND a.created_at >= @month_start
                      AND a.created_at < DATEADD(MONTH, 1, @month_start)
                      AND NOT EXISTS
                      (
                          SELECT 1
                          FROM dbo.analysis_quota_reservations AS r
                          WHERE r.analysis_id = a.id
                      );

                    IF @reserved_or_completed + @legacy_completed >= ?
                        THROW 51002, 'Limite mensal de análises atingido.', 1;

                    INSERT INTO dbo.analysis_quota_reservations
                        (id, user_id, month_start, status)
                    VALUES (?, ?, @month_start, N'RESERVED');
                    """,
                    f"MatchCV:MonthlyQuota:{user_id}",
                    str(user_id),
                    str(user_id),
                    self.FREE_ANALYSIS_LIMIT,
                    str(reservation_id),
                    str(user_id),
                )
                connection.commit()
                return reservation_id
            except Exception as exception:
                connection.rollback()
                if "51002" in str(exception) or "Limite mensal de análises atingido" in str(exception):
                    raise MonthlyQuotaExceeded("Você atingiu o limite de três análises neste mês.") from exception
                raise
            finally:
                cursor.close()

    def link_analysis(self, reservation_id: UUID, analysis_id: UUID) -> None:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "UPDATE dbo.analysis_quota_reservations SET analysis_id = ?, updated_at = SYSUTCDATETIME() WHERE id = ? AND status = N'RESERVED'",
                    str(analysis_id), str(reservation_id),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("A reserva da cota não foi encontrada.")
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    def reconcile_reservations(self) -> int:
        """
        Corrige reservas deixadas para trás por encerramentos inesperados.

        Análises pendentes/em processamento mantêm a reserva. Reservas sem
        análise são liberadas somente após 30 minutos.
        """
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE r
                    SET
                        status = CASE a.status
                            WHEN N'COMPLETED' THEN N'COMPLETED'
                            WHEN N'FAILED' THEN N'RELEASED'
                        END,
                        updated_at = SYSUTCDATETIME()
                    FROM dbo.analysis_quota_reservations AS r
                    INNER JOIN dbo.analyses AS a
                        ON a.id = r.analysis_id
                    WHERE r.status = N'RESERVED'
                      AND a.status IN (N'COMPLETED', N'FAILED');

                    DECLARE @reconciled_analysis_rows INT = @@ROWCOUNT;

                    UPDATE dbo.analysis_quota_reservations
                    SET
                        status = N'RELEASED',
                        updated_at = SYSUTCDATETIME()
                    WHERE status = N'RESERVED'
                      AND analysis_id IS NULL
                      AND created_at < DATEADD(
                          MINUTE,
                          -30,
                          SYSUTCDATETIME()
                      );

                    SELECT @reconciled_analysis_rows + @@ROWCOUNT;
                    """
                )
                row = cursor.fetchone()
                connection.commit()
                return int(row[0]) if row else 0
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    def complete_reservation_for_analysis(self, analysis_id: UUID) -> None:
        self._update_reservation_for_analysis(analysis_id, "COMPLETED")

    def release_reservation_for_analysis(self, analysis_id: UUID) -> None:
        self._update_reservation_for_analysis(analysis_id, "RELEASED")

    def _update_reservation_for_analysis(self, analysis_id: UUID, status: str) -> None:
        if status not in {"COMPLETED", "RELEASED"}:
            raise ValueError("Status de reserva inválido.")
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_quota_reservations
                    SET status = ?, updated_at = SYSUTCDATETIME()
                    WHERE analysis_id = ? AND status = N'RESERVED'
                    """,
                    status,
                    str(analysis_id),
                )
                connection.commit()
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
