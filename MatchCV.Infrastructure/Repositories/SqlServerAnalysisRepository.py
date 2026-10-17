import json
from typing import Optional
from uuid import UUID

from MatchCV.Application.Repositories.IAnalysisRepository import (
    IAnalysisRepository,
)
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)
from MatchCV.Infrastructure.Models.AnalysisRecord import (
    AnalysisRecord,
)


class SqlServerAnalysisRepository(IAnalysisRepository):
    """Implementação SQL Server do repositório de análises."""

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        self._database_connection = database_connection

    def add(
        self,
        analysis: Analysis,
        user_id: UUID,
    ) -> Analysis:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.analyses (
                        id,
                        user_id,
                        resume_id,
                        job_description_id,
                        status,
                        evidenced_requirements,
                        unevidenced_requirements,
                        gaps,
                        resume_issues,
                        suggestions
                    )
                    VALUES (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                    """,
                    str(analysis.id),
                    str(user_id),
                    str(analysis.resume_id),
                    str(analysis.job_description_id),
                    analysis.status.value,
                    json.dumps(
                        analysis.evidenced_requirements,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.unevidenced_requirements,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.gaps,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.resume_issues,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.suggestions,
                        ensure_ascii=False,
                    ),
                )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

        return analysis

    def get_by_id(
        self,
        analysis_id: UUID,
    ) -> Optional[Analysis]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        resume_id,
                        job_description_id,
                        status,
                        evidenced_requirements,
                        unevidenced_requirements,
                        gaps,
                        resume_issues,
                        suggestions,
                        created_at,
                        completed_at
                    FROM dbo.analyses
                    WHERE id = ?
                    """,
                    str(analysis_id),
                )

                row = cursor.fetchone()

            finally:
                cursor.close()

        if row is None:
            return None

        return self._map_row_to_analysis(row)

    def get_by_id_and_user(
        self,
        analysis_id: UUID,
        user_id: UUID,
    ) -> Optional[Analysis]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        resume_id,
                        job_description_id,
                        status,
                        evidenced_requirements,
                        unevidenced_requirements,
                        gaps,
                        resume_issues,
                        suggestions,
                        created_at,
                        completed_at
                    FROM dbo.analyses
                    WHERE id = ?
                      AND user_id = ?
                    """,
                    str(analysis_id),
                    str(user_id),
                )

                row = cursor.fetchone()

            finally:
                cursor.close()

        if row is None:
            return None

        return self._map_row_to_analysis(row)

    def list_by_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]:
        if limit <= 0:
            raise ValueError("O limite deve ser maior que zero.")

        if offset < 0:
            raise ValueError("O offset não pode ser negativo.")

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        resume_id,
                        job_description_id,
                        status,
                        evidenced_requirements,
                        unevidenced_requirements,
                        gaps,
                        resume_issues,
                        suggestions,
                        created_at,
                        completed_at
                    FROM dbo.analyses
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    OFFSET ? ROWS
                    FETCH NEXT ? ROWS ONLY
                    """,
                    str(user_id),
                    offset,
                    limit,
                )

                rows = cursor.fetchall()

            finally:
                cursor.close()

        return [
            self._map_row_to_analysis(row)
            for row in rows
        ]

    def claim_pending(
        self,
        limit: int = 10,
    ) -> list[Analysis]:
        """
        Reserva análises PENDING para processamento.

        O UPDATE utiliza UPDLOCK e READPAST para evitar que duas
        execuções do worker processem a mesma análise.
        """

        if limit <= 0:
            raise ValueError(
                "O limite de análises deve ser maior que zero."
            )

        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    ;WITH pending AS
                    (
                        SELECT TOP (?)
                            id
                        FROM dbo.analyses WITH (
                            UPDLOCK,
                            READPAST,
                            ROWLOCK
                        )
                        WHERE status = ?
                        ORDER BY created_at ASC
                    )
                    UPDATE analyses
                    SET status = ?
                    OUTPUT
                        inserted.id,
                        inserted.user_id,
                        inserted.resume_id,
                        inserted.job_description_id,
                        inserted.status,
                        inserted.evidenced_requirements,
                        inserted.unevidenced_requirements,
                        inserted.gaps,
                        inserted.resume_issues,
                        inserted.suggestions,
                        inserted.created_at,
                        inserted.completed_at
                    FROM dbo.analyses AS analyses
                    INNER JOIN pending
                        ON pending.id = analyses.id;
                    """,
                    limit,
                    AnalysisStatus.PENDING.value,
                    AnalysisStatus.PROCESSING.value,
                )

                rows = cursor.fetchall()

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

        return [
            self._map_row_to_analysis(row)
            for row in rows
        ]

    def update(
        self,
        analysis: Analysis,
    ) -> Analysis:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE dbo.analyses
                    SET
                        status = ?,
                        evidenced_requirements = ?,
                        unevidenced_requirements = ?,
                        gaps = ?,
                        resume_issues = ?,
                        suggestions = ?,
                        completed_at = ?
                    WHERE id = ?
                    """,
                    analysis.status.value,
                    json.dumps(
                        analysis.evidenced_requirements,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.unevidenced_requirements,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.gaps,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.resume_issues,
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        analysis.suggestions,
                        ensure_ascii=False,
                    ),
                    analysis.completed_at,
                    str(analysis.id),
                )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

            finally:
                cursor.close()

        return analysis

    @staticmethod
    def _map_row_to_analysis(row) -> Analysis:
        record = AnalysisRecord(
            id=UUID(str(row[0])),
            user_id=UUID(str(row[1])),
            resume_id=UUID(str(row[2])),
            job_description_id=UUID(str(row[3])),
            status=AnalysisStatus(row[4]),
            evidenced_requirements=json.loads(
                row[5] or "[]"
            ),
            unevidenced_requirements=json.loads(
                row[6] or "[]"
            ),
            gaps=json.loads(
                row[7] or "[]"
            ),
            resume_issues=json.loads(
                row[8] or "[]"
            ),
            suggestions=json.loads(
                row[9] or "[]"
            ),
            created_at=row[10],
            completed_at=row[11],
        )

        return Analysis(
            id=record.id,
            user_id=record.user_id,
            resume_id=record.resume_id,
            job_description_id=record.job_description_id,
            status=record.status,
            evidenced_requirements=record.evidenced_requirements,
            unevidenced_requirements=record.unevidenced_requirements,
            gaps=record.gaps,
            resume_issues=record.resume_issues,
            suggestions=record.suggestions,
            completed_at=record.completed_at,
        )
