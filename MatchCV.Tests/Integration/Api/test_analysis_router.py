from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from MatchCV.Api.Dependencies.AnalysisDependencies import (
    get_analyze_resume_use_case,
)
from MatchCV.Api.Routers.AnalysisRouter import (
    get_analysis_usage_repository,
)
from MatchCV.Api.main import app
from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Login.Authorization.CurrentUser import get_current_user


@pytest.fixture
def api_client():
    use_case = MagicMock()
    usage_repository = MagicMock()
    usage_repository.FREE_ANALYSIS_LIMIT = 3
    usage_repository.count_completed.return_value = 0
    use_case.authenticated_user_id = None

    current_user = User(
        id=uuid4(),
        name="Usuário de Teste",
        email="teste@example.com",
        password_hash="hash-de-teste",
        role=UserRole.USER,
    )

    app.dependency_overrides[get_analyze_resume_use_case] = (
        lambda: use_case
    )
    app.dependency_overrides[get_analysis_usage_repository] = (
        lambda: usage_repository
    )
    use_case.authenticated_user_id = current_user.id

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )

    try:
        with TestClient(app) as client:
            yield client, use_case, usage_repository
    finally:
        app.dependency_overrides.pop(
            get_analyze_resume_use_case,
            None,
        )
        app.dependency_overrides.pop(
            get_analysis_usage_repository,
            None,
        )
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )


def create_analysis_result():
    return AnalysisResult(
        evidenced_requirements=["Python", "APIs REST"],
        unevidenced_requirements=["Docker"],
        gaps=["Experiência com cloud"],
        resume_issues=["Poucos detalhes sobre projetos"],
        suggestions=["Detalhar responsabilidades"],
    )


class TestAnalysisRouter:
    def test_analyzes_resume_text_successfully(self, api_client):
        client, use_case, usage_repository = api_client
        use_case.execute.return_value = create_analysis_result()

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": (
                    "Experiência profissional com Python e APIs REST."
                ),
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": "completed",
            "evidenced_requirements": ["Python", "APIs REST"],
            "unevidenced_requirements": ["Docker"],
            "gaps": ["Experiência com cloud"],
            "resume_issues": ["Poucos detalhes sobre projetos"],
            "suggestions": ["Detalhar responsabilidades"],
        }

        use_case.execute.assert_called_once()
        assert use_case.execute.call_args.args[1] == (
            use_case.authenticated_user_id
        )

        request = use_case.execute.call_args.args[0]

        assert request.job_description == (
            "Vaga para desenvolvedor Python."
        )
        assert request.resume_text == (
            "Experiência profissional com Python e APIs REST."
        )
        assert request.file_stream is None

        usage_repository.record_success.assert_called_once_with(
            uuid4()
        ) if False else None

    def test_analyzes_uploaded_file_successfully(self, api_client):
        client, use_case, usage_repository = api_client
        use_case.execute.return_value = create_analysis_result()

        file_content = b"conteudo de teste do curriculo"

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
            },
            files={
                "resume": (
                    "curriculo.pdf",
                    file_content,
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        use_case.execute.assert_called_once()

        request = use_case.execute.call_args.args[0]

        assert request.job_description == (
            "Vaga para desenvolvedor Python."
        )
        assert request.resume_text is None
        assert request.file_name == "curriculo.pdf"
        assert request.file_size_bytes == len(file_content)
        assert request.file_stream.read() == file_content

        usage_repository.record_success.assert_called_once()

    def test_rejects_request_without_resume(self, api_client):
        client, use_case, usage_repository = api_client

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Cole o currículo ou escolha um arquivo antes de continuar."
        )

        use_case.execute.assert_not_called()
        usage_repository.record_success.assert_not_called()

    def test_rejects_request_with_blank_resume_text(self, api_client):
        client, use_case, usage_repository = api_client

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": "   ",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Cole o currículo ou escolha um arquivo antes de continuar."
        )

        use_case.execute.assert_not_called()
        usage_repository.record_success.assert_not_called()

    def test_rejects_text_and_file_together(self, api_client):
        client, use_case, usage_repository = api_client

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": "Currículo enviado como texto.",
            },
            files={
                "resume": (
                    "curriculo.pdf",
                    b"conteudo do arquivo",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Informe o currículo por texto ou por arquivo, não pelos dois."
        )

        use_case.execute.assert_not_called()
        usage_repository.record_success.assert_not_called()

    def test_rejects_empty_uploaded_file(self, api_client):
        client, use_case, usage_repository = api_client

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
            },
            files={
                "resume": (
                    "curriculo.pdf",
                    b"",
                    "application/pdf",
                ),
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "O arquivo do currículo está vazio."
        )

        use_case.execute.assert_not_called()
        usage_repository.record_success.assert_not_called()

    def test_returns_400_when_use_case_raises_domain_exception(
        self,
        api_client,
    ):
        client, use_case, usage_repository = api_client

        use_case.execute.side_effect = DomainException(
            "A descrição da vaga deve possuir pelo menos 30 caracteres úteis."
        )

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": (
                    "Experiência profissional com Python e APIs REST."
                ),
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "A descrição da vaga deve possuir pelo menos 30 caracteres úteis."
        )

        usage_repository.record_success.assert_not_called()

    def test_returns_503_when_provider_is_not_implemented(
        self,
        api_client,
    ):
        client, use_case, usage_repository = api_client

        use_case.execute.side_effect = NotImplementedError(
            "Provedor de IA ainda não implementado."
        )

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": (
                    "Experiência profissional com Python e APIs REST."
                ),
            },
        )

        assert response.status_code == 503
        assert response.json()["detail"] == (
            "Provedor de IA ainda não implementado."
        )

        usage_repository.record_success.assert_not_called()

    def test_returns_500_when_unexpected_error_occurs(
        self,
        api_client,
    ):
        client, use_case, usage_repository = api_client

        use_case.execute.side_effect = RuntimeError(
            "Erro interno de teste."
        )

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": (
                    "Experiência profissional com Python e APIs REST."
                ),
            },
        )

        assert response.status_code == 500
        assert response.json()["detail"] == (
            "Não foi possível concluir a análise."
        )

        usage_repository.record_success.assert_not_called()

    def test_rejects_request_without_job_description(self, api_client):
        client, use_case, usage_repository = api_client

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "resume_text": (
                    "Experiência profissional com Python e APIs REST."
                ),
            },
        )

        assert response.status_code == 422

        use_case.execute.assert_not_called()
        usage_repository.record_success.assert_not_called()

    def test_rejects_user_who_reached_free_analysis_limit(
        self,
        api_client,
    ):
        client, use_case, usage_repository = api_client
        usage_repository.count_completed.return_value = 3

        response = client.post(
            "/api/v1/analysis/resume",
            data={
                "job_description": "Vaga para desenvolvedor Python.",
                "resume_text": (
                    "Experiência profissional com Python e APIs REST."
                ),
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Você atingiu o limite de três análises concluídas "
            "da versão gratuita."
        )

        use_case.execute.assert_not_called()
        usage_repository.record_success.assert_not_called()
