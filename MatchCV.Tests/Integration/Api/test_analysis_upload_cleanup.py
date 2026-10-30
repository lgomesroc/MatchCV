from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient
from starlette.datastructures import UploadFile

from MatchCV.Api.Dependencies.AnalysisDependencies import get_analyze_resume_use_case
from MatchCV.Api.Routers.AnalysisRouter import get_analysis_usage_repository
from MatchCV.Api.main import app
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Login.Authorization.CurrentUser import get_current_user


def test_upload_is_closed_after_reading(monkeypatch):
    use_case = MagicMock()
    usage_repository = MagicMock()
    current_user = User(
        id=uuid4(),
        name="Synthetic Test User",
        email="upload-cleanup@example.test",
        password_hash="synthetic-hash",
        role=UserRole.ADMIN,
    )
    use_case.enqueue.return_value = Analysis(
        id=uuid4(),
        user_id=current_user.id,
        resume_id=uuid4(),
        job_description_id=uuid4(),
        status=AnalysisStatus.PENDING,
    )
    app.dependency_overrides[get_analyze_resume_use_case] = lambda: use_case
    app.dependency_overrides[get_analysis_usage_repository] = lambda: usage_repository
    app.dependency_overrides[get_current_user] = lambda: current_user
    close_spy = AsyncMock()
    monkeypatch.setattr(UploadFile, "close", close_spy)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/analysis/resume",
                data={"job_description": "Synthetic backend developer role."},
                files={"resume": ("synthetic.pdf", b"synthetic test content", "application/pdf")},
            )
        assert response.status_code == 202
        assert close_spy.await_count >= 1
    finally:
        for dependency in (
            get_analyze_resume_use_case,
            get_analysis_usage_repository,
            get_current_user,
        ):
            app.dependency_overrides.pop(dependency, None)
