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
    ) -> Analysis:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.analyses (
                        id,
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
                        ?
                    )
                    """,
                    str(analysis.id),
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

        record = AnalysisRecord(
            id=UUID(str(row[0])),
            resume_id=UUID(str(row[1])),
            job_description_id=UUID(str(row[2])),
            status=AnalysisStatus(row[3]),
            evidenced_requirements=json.loads(
                row[4] or "[]"
            ),
            unevidenced_requirements=json.loads(
                row[5] or "[]"
            ),
            gaps=json.loads(
                row[6] or "[]"
            ),
            resume_issues=json.loads(
                row[7] or "[]"
            ),
            suggestions=json.loads(
                row[8] or "[]"
            ),
            created_at=row[9],
            completed_at=row[10],
        )

        return Analysis(
            id=record.id,
            resume_id=record.resume_id,
            job_description_id=record.job_description_id,
            status=record.status,
            evidenced_requirements=record.evidenced_requirements,
            unevidenced_requirements=record.unevidenced_requirements,
            gaps=record.gaps,
            resume_issues=record.resume_issues,
            suggestions=record.suggestions,
        )

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
