from datetime import datetime, timezone
from uuid import uuid4

import pytest

from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Domain.Exceptions.DomainException import DomainException


def create_valid_analysis():
    return Analysis.create(
        resume_id=uuid4(),
        job_description_id=uuid4(),
    )


def test_create_starts_with_pending_status():
    result = create_valid_analysis()

    assert result.id is not None
    assert result.status == AnalysisStatus.PENDING
    assert result.completed_at is None
    assert result.evidenced_requirements == []
    assert result.unevidenced_requirements == []
    assert result.gaps == []
    assert result.resume_issues == []
    assert result.suggestions == []


def test_create_rejects_missing_resume_id():
    with pytest.raises(DomainException):
        Analysis.create(
            resume_id=None,
            job_description_id=uuid4(),
        )


def test_create_rejects_missing_job_description_id():
    with pytest.raises(DomainException):
        Analysis.create(
            resume_id=uuid4(),
            job_description_id=None,
        )


def test_start_processing_changes_status_to_processing():
    analysis = create_valid_analysis()

    analysis.start_processing()

    assert analysis.status == AnalysisStatus.PROCESSING


def test_start_processing_rejects_non_pending_analysis():
    analysis = create_valid_analysis()
    analysis.start_processing()

    with pytest.raises(DomainException):
        analysis.start_processing()


def test_complete_updates_results_and_completion_timestamp():
    analysis = create_valid_analysis()
    analysis.start_processing()

    evidenced = ["Python comprovado no currículo"]
    unevidenced = ["Experiência com Kubernetes não evidenciada"]
    gaps = ["Não há evidência de Kubernetes"]
    issues = ["Falta detalhar resultados profissionais"]
    suggestions = ["Adicionar projetos relevantes, se existentes"]

    analysis.complete(
        evidenced_requirements=evidenced,
        unevidenced_requirements=unevidenced,
        gaps=gaps,
        resume_issues=issues,
        suggestions=suggestions,
    )

    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.evidenced_requirements == evidenced
    assert analysis.unevidenced_requirements == unevidenced
    assert analysis.gaps == gaps
    assert analysis.resume_issues == issues
    assert analysis.suggestions == suggestions
    assert analysis.completed_at is not None
    assert analysis.completed_at.tzinfo is not None


def test_complete_rejects_analysis_that_is_not_processing():
    analysis = create_valid_analysis()

    with pytest.raises(DomainException):
        analysis.complete(
            evidenced_requirements=[],
            unevidenced_requirements=[],
            gaps=[],
            resume_issues=[],
            suggestions=[],
        )


def test_fail_changes_status_and_sets_completion_timestamp():
    analysis = create_valid_analysis()
    analysis.start_processing()

    analysis.fail()

    assert analysis.status == AnalysisStatus.FAILED
    assert analysis.completed_at is not None
    assert analysis.completed_at.tzinfo is not None


def test_fail_rejects_analysis_that_is_not_processing():
    analysis = create_valid_analysis()

    with pytest.raises(DomainException):
        analysis.fail()


def test_completed_timestamp_is_timezone_aware():
    analysis = create_valid_analysis()
    analysis.start_processing()
    analysis.fail()

    assert isinstance(analysis.completed_at, datetime)
    assert analysis.completed_at.utcoffset() == timezone.utc.utcoffset(
        analysis.completed_at
    )
