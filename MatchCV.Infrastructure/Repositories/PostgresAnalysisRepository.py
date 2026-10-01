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
from MatchCV.Infrastructure.Models.AnalysisRecord import AnalysisRecord


class PostgresAnalysisRepository(IAnalysisRepository):
    """Implementação PostgreSQL do repositório de análises."""

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
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO analyses (
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
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        analysis.id,
                        analysis.resume_id,
                        analysis.job_description_id,
                        analysis.status.value,
                        analysis.evidenced_requirements,
                        analysis.unevidenced_requirements,
                        analysis.gaps,
                        analysis.resume_issues,
                        analysis.suggestions,
                    ),
                )

            connection.commit()

        return analysis

    def get_by_id(
        self,
        analysis_id: UUID,
    ) -> Optional[Analysis]:
        with self._database_connection.connection() as connection:
            with connection.cursor() as cursor:
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
                    FROM analyses
                    WHERE id = %s
                    """,
                    (analysis_id,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        record = AnalysisRecord(
            id=row[0],
            resume_id=row[1],
            job_description_id=row[2],
            status=AnalysisStatus(row[3]),
            evidenced_requirements=row[4] or [],
            unevidenced_requirements=row[5] or [],
            gaps=row[6] or [],
            resume_issues=row[7] or [],
            suggestions=row[8] or [],
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
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE analyses
                    SET
                        status = %s,
                        evidenced_requirements = %s,
                        unevidenced_requirements = %s,
                        gaps = %s,
                        resume_issues = %s,
                        suggestions = %s,
                        completed_at = %s
                    WHERE id = %s
                    """,
                    (
                        analysis.status.value,
                        analysis.evidenced_requirements,
                        analysis.unevidenced_requirements,
                        analysis.gaps,
                        analysis.resume_issues,
                        analysis.suggestions,
                        analysis.completed_at,
                        analysis.id,
                    ),
                )

            connection.commit()

        return analysis
