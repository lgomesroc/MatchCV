from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional
from uuid import UUID, uuid4

from MatchCV.Application.Queue.AnalysisQueueItem import (
    AnalysisQueueItem,
)
from MatchCV.Application.Queue.IAnalysisQueueRepository import (
    IAnalysisQueueRepository,
)
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)


class SqlServerAnalysisQueueRepository(
    IAnalysisQueueRepository
):
    """Implementação SQL Server da fila de análises."""

    PROCESSING_TIMEOUT_MINUTES = 15

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        self._database_connection = database_connection

    @contextmanager
    def exclusive_processing(self) -> Iterator[None]:
        """Serializa workers por meio de um bloqueio global do SQL Server."""
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()
            acquired = False
            try:
                cursor.execute(
                    """
                    DECLARE @result INT;
                    EXEC @result = sys.sp_getapplock
                        @Resource = N'MatchCV:AnalysisWorker:Global',
                        @LockMode = N'Exclusive',
                        @LockOwner = N'Session',
                        @LockTimeout = -1;
                    SELECT @result;
                    """
                )
                row = cursor.fetchone()
                if row is None or int(row[0]) < 0:
                    raise RuntimeError("Não foi possível obter o bloqueio global da fila.")
                acquired = True
                yield
            finally:
                if acquired:
                    try:
                        cursor.execute(
                            """
                            EXEC sys.sp_releaseapplock
                                @Resource = N'MatchCV:AnalysisWorker:Global',
                                @LockOwner = N'Session';
                            """
                        )
                    finally:
                        cursor.close()
                else:
                    cursor.close()

    def enqueue(
        self,
        analysis_id: UUID,
        payload_ciphertext: bytes,
    ) -> AnalysisQueueItem:
        queue_id = uuid4()

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.analysis_queue (
                        id,
                        analysis_id,
                        payload_ciphertext,
                        status,
                        attempts
                    )
                    VALUES (?, ?, ?, N'PENDING', 0)
                    """,
                    str(queue_id),
                    str(analysis_id),
                    payload_ciphertext,
                )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

        return AnalysisQueueItem(
            id=queue_id,
            analysis_id=analysis_id,
            payload_ciphertext=payload_ciphertext,
            status="PENDING",
            attempts=0,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            finished_at=None,
            last_error=None,
        )

    def get_next_pending(
        self,
    ) -> Optional[AnalysisQueueItem]:
        """
        Reserva atomicamente a próxima tarefa pendente.
        """

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    ;WITH next_item AS
                    (
                        SELECT TOP (1) id
                        FROM dbo.analysis_queue WITH (
                            UPDLOCK,
                            READPAST,
                            ROWLOCK
                        )
                        WHERE status = N'PENDING'
                        ORDER BY created_at ASC, id ASC
                    )
                    UPDATE queue
                    SET
                        status = N'PROCESSING',
                        attempts = attempts + 1,
                        started_at = SYSUTCDATETIME(),
                        last_error = NULL
                    OUTPUT
                        inserted.id,
                        inserted.analysis_id,
                        inserted.payload_ciphertext,
                        inserted.status,
                        inserted.attempts,
                        inserted.created_at,
                        inserted.started_at,
                        inserted.finished_at,
                        inserted.last_error
                    FROM dbo.analysis_queue AS queue
                    INNER JOIN next_item
                        ON next_item.id = queue.id;
                    """
                )

                row = cursor.fetchone()
                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

        if row is None:
            return None

        return AnalysisQueueItem(
            id=UUID(str(row[0])),
            analysis_id=UUID(str(row[1])),
            payload_ciphertext=bytes(row[2]),
            status=row[3],
            attempts=int(row[4]),
            created_at=row[5],
            started_at=row[6],
            finished_at=row[7],
            last_error=row[8],
        )

    def renew_processing(
        self,
        queue_id: UUID,
    ) -> bool:
        """
        Renova o lease de uma tarefa em processamento.

        Deve ser chamada periodicamente pelo worker enquanto
        a análise estiver sendo executada.

        Retorna False se a tarefa não estiver mais em PROCESSING.
        """

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_queue
                    SET started_at = SYSUTCDATETIME()
                    WHERE id = ?
                      AND status = N'PROCESSING'
                    """,
                    str(queue_id),
                )

                renewed = cursor.rowcount == 1
                connection.commit()

                return renewed

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

    def mark_processing(
        self,
        queue_id: UUID,
    ) -> None:
        """
        Mantido para compatibilidade com chamadas existentes.

        No fluxo atual, get_next_pending() já reserva a tarefa.
        O worker não deve chamar este método novamente.
        """

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_queue
                    SET
                        status = N'PROCESSING',
                        attempts = attempts + 1,
                        started_at = SYSUTCDATETIME(),
                        last_error = NULL
                    WHERE id = ?
                      AND status = N'PENDING'
                    """,
                    str(queue_id),
                )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

    def mark_completed(
        self,
        queue_id: UUID,
    ) -> None:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_queue
                    SET
                        status = N'COMPLETED',
                        finished_at = SYSUTCDATETIME(),
                        payload_ciphertext = 0x,
                        last_error = NULL
                    WHERE id = ?
                      AND status = N'PROCESSING'
                    """,
                    str(queue_id),
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "A tarefa não estava em PROCESSING "
                        "ou não foi encontrada."
                    )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

    def mark_failed(
        self,
        queue_id: UUID,
        error: str,
    ) -> None:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_queue
                    SET
                        status = N'FAILED',
                        finished_at = SYSUTCDATETIME(),
                        payload_ciphertext = 0x,
                        last_error = ?
                    WHERE id = ?
                      AND status = N'PROCESSING'
                    """,
                    error[:1000],
                    str(queue_id),
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "A tarefa não estava em PROCESSING "
                        "ou não foi encontrada."
                    )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

    def recover_processing(self) -> int:
        """
        Recupera tarefas cujo lease expirou.

        O worker deve renovar started_at periodicamente.
        Uma tarefa sem renovação por mais de 15 minutos
        poderá voltar para PENDING.
        """

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.analysis_queue
                    SET
                        status = N'PENDING',
                        started_at = NULL,
                        last_error = N'Lease expirado; tarefa recuperada.'
                    WHERE status = N'PROCESSING'
                      AND started_at < DATEADD(
                          MINUTE,
                          ?,
                          SYSUTCDATETIME()
                      )
                    """,
                    -self.PROCESSING_TIMEOUT_MINUTES,
                )

                affected = max(cursor.rowcount, 0)
                connection.commit()

                return affected

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()
