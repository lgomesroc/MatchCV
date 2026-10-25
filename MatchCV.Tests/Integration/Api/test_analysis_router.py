from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from MatchCV.Api.Dependencies.AnalysisDependencies import get_analyze_resume_use_case
from MatchCV.Api.Routers.AnalysisRouter import get_analysis_repository, get_analysis_usage_repository
from MatchCV.Api.main import app
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.AnalysisStatus import AnalysisStatus
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Login.Authorization.CurrentUser import get_current_user
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisUsageRepository import MonthlyQuotaExceeded


@pytest.fixture
def api_client():
    use_case = MagicMock()
    usage_repository = MagicMock()
    usage_repository.FREE_ANALYSIS_LIMIT = 3
    usage_repository.count_completed.return_value = 0
    analysis_repository = MagicMock()
    current_user = User(
        id=uuid4(),
        name="Usuário de Teste",
        email="teste@example.com",
        password_hash="hash-de-teste",
        role=UserRole.USER,
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
    app.dependency_overrides[get_analysis_repository] = lambda: analysis_repository
    app.dependency_overrides[get_current_user] = lambda: current_user
    try:
        with TestClient(app) as client:
            yield client, use_case, usage_repository, analysis_repository, current_user
    finally:
        for dependency in (
            get_analyze_resume_use_case,
            get_analysis_usage_repository,
            get_analysis_repository,
            get_current_user,
        ):
            app.dependency_overrides.pop(dependency, None)


class TestAnalysisRouter:
    def test_enqueues_resume_text_and_returns_accepted(self, api_client):
        client, use_case, usage_repository, _, current_user = api_client

        def enqueue_and_link(request, user_id, on_analysis_created=None):
            analysis = use_case.enqueue.return_value
            if on_analysis_created is not None:
                on_analysis_created(analysis.id)
            return analysis

        use_case.enqueue.side_effect = enqueue_and_link
        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": "Experiência profissional com Python e APIs REST.",
            },
        )
        assert response.status_code == 202
        body = response.json()
        assert body["status"] == "pending"
        assert body["analysis_id"] == str(use_case.enqueue.return_value.id)
        use_case.enqueue.assert_called_once()
        request = use_case.enqueue.call_args.args[0]
        assert request.job_description == "Vaga para desenvolvedor Python."
        assert request.resume_text == "Experiência profissional com Python e APIs REST."
        assert use_case.enqueue.call_args.kwargs["user_id"] == current_user.id
        usage_repository.link_analysis.assert_called_once_with(
            usage_repository.reserve_monthly_slot.return_value,
            use_case.enqueue.return_value.id,
        )

    def test_enqueues_uploaded_file(self, api_client):
        client, use_case, _, _, _ = api_client
        file_content = b"test resume content"
        response = client.post(
            "/api/v1/analysis/resume",
            data={"job_description": "Vaga para desenvolvedor Python."},
            files={"resume": ("curriculo.pdf", file_content, "application/pdf")},
        )
        assert response.status_code == 202
        request = use_case.enqueue.call_args.args[0]
        assert request.file_name == "curriculo.pdf"
        assert request.file_size_bytes == len(file_content)
        assert request.file_stream.read() == file_content

    @pytest.mark.parametrize(
        ("data", "files", "expected_detail"),
        [
            ({"job_description": "Vaga"}, None, "Cole o currículo ou escolha um arquivo antes de continuar."),
            ({"job_description": "Vaga", "resume_text": "   "}, None, "Cole o currículo ou escolha um arquivo antes de continuar."),
            ({"job_description": "Vaga", "resume_text": "texto"}, {"resume": ("curriculo.pdf", b"arquivo", "application/pdf")}, "Informe o currículo por texto ou por arquivo, não pelos dois."),
            ({"job_description": "Vaga"}, {"resume": ("curriculo.pdf", b"", "application/pdf")}, "O arquivo do currículo está vazio."),
        ],
    )
    def test_rejects_invalid_resume_input(self, api_client, data, files, expected_detail):
        client, use_case, _, _, _ = api_client
        response = client.post("/api/v1/analysis/resume", data=data, files=files)
        assert response.status_code == 400
        assert response.json()["detail"] == expected_detail
        use_case.enqueue.assert_not_called()

    def test_enforces_free_analysis_limit(self, api_client):
        client, use_case, usage_repository, _, _ = api_client
        usage_repository.reserve_monthly_slot.side_effect = MonthlyQuotaExceeded(
            "Você atingiu o limite de três análises neste mês."
        )
        response = client.post(
            "/api/v1/analysis/resume",
            data={"job_description": "Vaga para desenvolvedor Python.", "resume_text": "Currículo válido."},
        )
        assert response.status_code == 403
        use_case.enqueue.assert_not_called()

    def test_returns_domain_validation_error(self, api_client):
        client, use_case, _, _, _ = api_client
        use_case.enqueue.side_effect = DomainException("Currículo inválido.")
        response = client.post(
            "/api/v1/analysis/resume",
            data={"job_description": "Vaga para desenvolvedor Python.", "resume_text": "Currículo válido."},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Currículo inválido."

    def test_status_endpoint_returns_only_current_users_analysis(self, api_client):
        client, _, _, repository, current_user = api_client
        analysis = Analysis(
            id=uuid4(),
            user_id=current_user.id,
            resume_id=uuid4(),
            job_description_id=uuid4(),
            status=AnalysisStatus.COMPLETED,
            evidenced_requirements=["Python"],
        )
        repository.get_by_id_and_user.return_value = analysis
        response = client.get(f"/api/v1/analysis/{analysis.id}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert response.json()["evidenced_requirements"] == ["Python"]
        repository.get_by_id_and_user.assert_called_once_with(analysis.id, current_user.id)

    def test_status_endpoint_hides_analysis_owned_by_another_user(self, api_client):
        client, _, _, repository, _ = api_client
        repository.get_by_id_and_user.return_value = None
        response = client.get(f"/api/v1/analysis/{uuid4()}")
        assert response.status_code == 404
