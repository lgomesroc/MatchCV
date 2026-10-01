from typing import Optional
from uuid import UUID

from MatchCV.Application.Repositories.IJobDescriptionRepository import (
    IJobDescriptionRepository,
)
from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Infrastructure.Database.DatabaseConnection import (
    DatabaseConnection,
)
from MatchCV.Infrastructure.Models.JobDescriptionRecord import (
    JobDescriptionRecord,
)


class SqlServerJobDescriptionRepository(
    IJobDescriptionRepository
):
    """Implementação SQL Server do repositório de vagas."""

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        self._database_connection = database_connection

    def add(
        self,
        job_description: JobDescription,
    ) -> JobDescription:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO dbo.job_descriptions (
                        id,
                        content
                    )
                    VALUES (
                        ?,
                        ?
                    )
                    """,
                    str(job_description.id),
                    job_description.content,
                )

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

        return job_description

    def get_by_id(
        self,
        job_description_id: UUID,
    ) -> Optional[JobDescription]:
        with self._database_connection.connection() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    SELECT
                        id,
                        content,
                        created_at
                    FROM dbo.job_descriptions
                    WHERE id = ?
                    """,
                    str(job_description_id),
                )

                row = cursor.fetchone()
            finally:
                cursor.close()

        if row is None:
            return None

        record = JobDescriptionRecord(
            id=UUID(str(row[0])),
            content=row[1],
            created_at=row[2],
        )

        return JobDescription(
            id=record.id,
            content=record.content,
        )
