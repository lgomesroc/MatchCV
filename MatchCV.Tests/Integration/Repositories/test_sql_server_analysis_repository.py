
from uuid import uuid4

from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisRepository import (
    SqlServerAnalysisRepository,
)
from MatchCV.Infrastructure.Repositories.SqlServerJobDescriptionRepository import (
    SqlServerJobDescriptionRepository,
)


class TestSqlServerAnalysisRepository:
    def test_add_and_get_by_id(
        self,
        test_database_connection: DatabaseConnection,
        cleanup_registry,
    ):
        job_repository = SqlServerJobDescriptionRepository(
            database_connection=test_database_connection,
        )
        analysis_repository = SqlServerAnalysisRepository(
            database_connection=test_database_connection,
        )

        job_description = JobDescription.create(
            "Desenvolvedor Python com experiência em APIs REST e SQL Server."
        )
        cleanup_registry["job_description_ids"].append(
            job_description.id
        )
        job_repository.add(job_description)

        analysis = Analysis.create(
            resume_id=uuid4(),
            job_description_id=job_description.id,
        )
        cleanup_registry["analysis_ids"].append(analysis.id)

        added = analysis_repository.add(analysis)

        assert added.id == analysis.id

        retrieved = analysis_repository.get_by_id(analysis.id)

        assert retrieved is not None
        assert retrieved.id == analysis.id
        assert retrieved.resume_id == analysis.resume_id
        assert retrieved.job_description_id == job_description.id
        assert retrieved.status == AnalysisStatus.PENDING
        assert retrieved.evidenced_requirements == []
        assert retrieved.unevidenced_requirements == []
        assert retrieved.gaps == []
        assert retrieved.resume_issues == []
        assert retrieved.suggestions == []
        assert retrieved.completed_at is None

    def test_update_persists_completed_analysis(
        self,
        test_database_connection: DatabaseConnection,
        cleanup_registry,
    ):
        job_repository = SqlServerJobDescriptionRepository(
            database_connection=test_database_connection,
        )
        analysis_repository = SqlServerAnalysisRepository(
            database_connection=test_database_connection,
        )

        job_description = JobDescription.create(
            "Desenvolvedor Python com experiência em APIs REST e SQL Server."
        )
        cleanup_registry["job_description_ids"].append(
            job_description.id
        )
        job_repository.add(job_description)

        analysis = Analysis.create(
            resume_id=uuid4(),
            job_description_id=job_description.id,
        )
        cleanup_registry["analysis_ids"].append(analysis.id)

        analysis_repository.add(analysis)

        analysis.start_processing()
        analysis.complete(
            evidenced_requirements=[
                "Python",
                "APIs REST",
                "SQL Server",
            ],
            unevidenced_requirements=["Docker"],
            gaps=["Experiência com cloud"],
            resume_issues=["Descrição genérica das atividades"],
            suggestions=["Detalhar projetos realizados"],
        )

        updated = analysis_repository.update(analysis)

        assert updated.id == analysis.id
        assert updated.status == AnalysisStatus.COMPLETED

        retrieved = analysis_repository.get_by_id(analysis.id)

        assert retrieved is not None
        assert retrieved.status == AnalysisStatus.COMPLETED
        assert retrieved.evidenced_requirements == [
            "Python",
            "APIs REST",
            "SQL Server",
        ]
        assert retrieved.unevidenced_requirements == ["Docker"]
        assert retrieved.gaps == ["Experiência com cloud"]
        assert retrieved.resume_issues == [
            "Descrição genérica das atividades"
        ]
        assert retrieved.suggestions == [
            "Detalhar projetos realizados"
        ]
        assert retrieved.completed_at is not None

    def test_get_by_id_returns_none_when_record_does_not_exist(
        self,
        test_database_connection: DatabaseConnection,
    ):
        repository = SqlServerAnalysisRepository(
            database_connection=test_database_connection,
        )

        result = repository.get_by_id(uuid4())

        assert result is None
