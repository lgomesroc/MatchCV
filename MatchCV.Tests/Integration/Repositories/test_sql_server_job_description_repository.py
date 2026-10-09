
from uuid import uuid4

from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection
from MatchCV.Infrastructure.Repositories.SqlServerJobDescriptionRepository import (
    SqlServerJobDescriptionRepository,
)


class TestSqlServerJobDescriptionRepository:
    def test_add_and_get_by_id(
        self,
        test_database_connection: DatabaseConnection,
        cleanup_registry,
    ):
        repository = SqlServerJobDescriptionRepository(
            database_connection=test_database_connection,
        )
        job_description = JobDescription.create(
            "Desenvolvedor Python com experiência em APIs REST e SQL Server."
        )
        cleanup_registry["job_description_ids"].append(job_description.id)

        added = repository.add(job_description)

        assert added.id == job_description.id
        assert added.content == job_description.content

        retrieved = repository.get_by_id(job_description.id)

        assert retrieved is not None
        assert retrieved.id == job_description.id
        assert retrieved.content == job_description.content

    def test_get_by_id_returns_none_when_record_does_not_exist(
        self,
        test_database_connection: DatabaseConnection,
    ):
        repository = SqlServerJobDescriptionRepository(
            database_connection=test_database_connection,
        )

        result = repository.get_by_id(uuid4())

        assert result is None
