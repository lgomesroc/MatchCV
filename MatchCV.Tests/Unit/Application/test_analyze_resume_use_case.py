from importlib import import_module
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult
from MatchCV.Application.DTOs.AnalyzeResumeRequest import (
    AnalyzeResumeRequest,
)
from MatchCV.Application.DTOs.ParsedResumeResult import ParsedResumeResult
from MatchCV.Application.UseCases.AnalyzeResumeUseCase import (
    AnalyzeResumeUseCase,
)
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Domain.Entities.Resume import Resume
from MatchCV.Domain.Enums.FileType import FileType
from MatchCV.Domain.Exceptions.DomainException import DomainException


use_case_module = import_module(
    "MatchCV.Application.UseCases.AnalyzeResumeUseCase"
)


VALID_RESUME_TEXT = (
    "Experiência profissional em desenvolvimento de sistemas, "
    "criação de APIs, manutenção de aplicações e testes automatizados."
)

VALID_JOB_DESCRIPTION = (
    "Vaga para desenvolvedor de software com experiência em APIs "
    "e desenvolvimento de aplicações."
)


def create_analysis_result():
    return AnalysisResult(
        evidenced_requirements=["Experiência com APIs"],
        unevidenced_requirements=["Experiência com cloud"],
        gaps=["Conhecimento em infraestrutura cloud"],
        resume_issues=["Descrição pouco detalhada de um projeto"],
        suggestions=["Detalhar os projetos desenvolvidos"],
    )


def create_use_case():
    parser_service = MagicMock()
    analysis_provider = MagicMock()
    job_description_repository = MagicMock()
    analysis_repository = MagicMock()

    use_case = AnalyzeResumeUseCase(
        resume_parser_service=parser_service,
        analysis_provider=analysis_provider,
        job_description_repository=job_description_repository,
        analysis_repository=analysis_repository,
    )

    return (
        use_case,
        parser_service,
        analysis_provider,
        job_description_repository,
        analysis_repository,
    )


def configure_entity_factories(monkeypatch):
    job_description = MagicMock()
    job_description.id = "job-description-id"
    job_description.content = VALID_JOB_DESCRIPTION

    resume = MagicMock()
    resume.id = "resume-id"

    analysis = MagicMock()
    analysis.id = "analysis-id"

    monkeypatch.setattr(
        use_case_module.JobDescription,
        "create",
        MagicMock(return_value=job_description),
    )
    monkeypatch.setattr(
        use_case_module.Resume,
        "create",
        MagicMock(return_value=resume),
    )
    monkeypatch.setattr(
        use_case_module.Analysis,
        "create",
        MagicMock(return_value=analysis),
    )

    return job_description, resume, analysis


class TestAnalyzeResumeUseCase:
    def test_executes_analysis_using_pasted_resume_text(
        self,
        monkeypatch,
    ):
        job_description, _, analysis = configure_entity_factories(
            monkeypatch
        )
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        expected_result = create_analysis_result()
        analysis_provider.analyze.return_value = expected_result

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
            resume_text=VALID_RESUME_TEXT,
        )

        result = use_case.execute(request)

        assert result is expected_result

        parser_service.parse.assert_not_called()

        analysis_provider.analyze.assert_called_once_with(
            resume_text=VALID_RESUME_TEXT,
            job_description=job_description.content,
        )

        job_repository.add.assert_called_once_with(job_description)
        analysis_repository.add.assert_called_once_with(analysis)

        assert analysis_repository.update.call_count == 2

        analysis.start_processing.assert_called_once_with()
        analysis.complete.assert_called_once_with(
            evidenced_requirements=expected_result.evidenced_requirements,
            unevidenced_requirements=expected_result.unevidenced_requirements,
            gaps=expected_result.gaps,
            resume_issues=expected_result.resume_issues,
            suggestions=expected_result.suggestions,
        )

        analysis.fail.assert_not_called()

    def test_executes_analysis_using_uploaded_file(
        self,
        monkeypatch,
    ):
        job_description, resume, analysis = configure_entity_factories(
            monkeypatch
        )
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        file_stream = BytesIO(b"fake resume content")

        parsed_resume = ParsedResumeResult(
            file_name="curriculo.pdf",
            file_type=FileType.PDF,
            file_size_bytes=1024,
            page_count=1,
            extracted_text=VALID_RESUME_TEXT,
            is_text_extractable=True,
            is_single_column=True,
            has_images=False,
            is_password_protected=False,
        )

        parser_service.parse.return_value = parsed_resume

        expected_result = create_analysis_result()
        analysis_provider.analyze.return_value = expected_result

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
            file_stream=file_stream,
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

        result = use_case.execute(request)

        assert result is expected_result

        parser_service.parse.assert_called_once_with(
            file_stream=file_stream,
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

        use_case_module.Resume.create.assert_called_once_with(
            file_name=parsed_resume.file_name,
            file_type=parsed_resume.file_type,
            file_size_bytes=parsed_resume.file_size_bytes,
            page_count=parsed_resume.page_count,
            extracted_text=VALID_RESUME_TEXT,
        )

        analysis_provider.analyze.assert_called_once_with(
            resume_text=VALID_RESUME_TEXT,
            job_description=job_description.content,
        )

        job_repository.add.assert_called_once_with(job_description)
        analysis_repository.add.assert_called_once_with(analysis)
        assert analysis_repository.update.call_count == 2

        analysis.complete.assert_called_once()
        analysis.fail.assert_not_called()

        assert resume.id == "resume-id"

    def test_rejects_request_without_resume_text_or_file(
        self,
        monkeypatch,
    ):
        configure_entity_factories(monkeypatch)
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
        )

        with pytest.raises(
            DomainException,
            match="dados do arquivo do currículo são obrigatórios",
        ):
            use_case.execute(request)

        parser_service.parse.assert_not_called()
        analysis_provider.analyze.assert_not_called()
        job_repository.add.assert_not_called()
        analysis_repository.add.assert_not_called()
        analysis_repository.update.assert_not_called()

    @pytest.mark.parametrize(
        "resume_text",
        [
            None,
            "",
            "   ",
        ],
    )
    def test_rejects_empty_resume_text(self, resume_text):
        with pytest.raises(
            DomainException,
            match="O currículo deve possuir texto",
        ):
            AnalyzeResumeUseCase._validate_resume_text(resume_text)

    @pytest.mark.parametrize(
        "resume_text",
        [
            "abc",
            "12345678901234567890123456789",
            "   abc  ",
        ],
    )
    def test_rejects_resume_with_fewer_than_30_useful_characters(
        self,
        resume_text,
    ):
        with pytest.raises(
            DomainException,
            match="30 caracteres úteis",
        ):
            AnalyzeResumeUseCase._validate_resume_text(resume_text)

    def test_strips_whitespace_from_valid_resume_text(self):
        resume_text = f"   {VALID_RESUME_TEXT}   "

        result = AnalyzeResumeUseCase._validate_resume_text(
            resume_text
        )

        assert result == VALID_RESUME_TEXT

    def test_rejects_resume_text_containing_emoji(self):
        resume_text = VALID_RESUME_TEXT + " 😀"

        with pytest.raises(DomainException):
            AnalyzeResumeUseCase._validate_resume_text(resume_text)

    def test_does_not_call_provider_when_resume_validation_fails(
        self,
        monkeypatch,
    ):
        configure_entity_factories(monkeypatch)
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
            resume_text="texto curto",
        )

        with pytest.raises(DomainException):
            use_case.execute(request)

        parser_service.parse.assert_not_called()
        analysis_provider.analyze.assert_not_called()
        job_repository.add.assert_not_called()
        analysis_repository.add.assert_not_called()
        analysis_repository.update.assert_not_called()

    def test_marks_analysis_as_failed_when_provider_raises(
        self,
        monkeypatch,
    ):
        _, _, analysis = configure_entity_factories(monkeypatch)
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        analysis_provider.analyze.side_effect = RuntimeError(
            "Falha no provedor de IA"
        )

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
            resume_text=VALID_RESUME_TEXT,
        )

        with pytest.raises(
            RuntimeError,
            match="Falha no provedor de IA",
        ):
            use_case.execute(request)

        analysis.start_processing.assert_called_once_with()
        analysis.fail.assert_called_once_with()
        analysis.complete.assert_not_called()

        assert analysis_repository.update.call_count == 2
        job_repository.add.assert_called_once()
        analysis_repository.add.assert_called_once()

        parser_service.parse.assert_not_called()

    def test_propagates_error_when_parser_fails(
        self,
        monkeypatch,
    ):
        configure_entity_factories(monkeypatch)
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        parser_service.parse.side_effect = RuntimeError(
            "Falha ao processar currículo"
        )

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
            file_stream=BytesIO(b"fake file"),
            file_name="curriculo.pdf",
            file_size_bytes=1024,
        )

        with pytest.raises(
            RuntimeError,
            match="Falha ao processar currículo",
        ):
            use_case.execute(request)

        parser_service.parse.assert_called_once()
        analysis_provider.analyze.assert_not_called()
        job_repository.add.assert_not_called()
        analysis_repository.add.assert_not_called()
        analysis_repository.update.assert_not_called()

    def test_rejects_request_with_missing_file_metadata(
        self,
        monkeypatch,
    ):
        configure_entity_factories(monkeypatch)
        (
            use_case,
            parser_service,
            analysis_provider,
            job_repository,
            analysis_repository,
        ) = create_use_case()

        request = AnalyzeResumeRequest(
            job_description=VALID_JOB_DESCRIPTION,
            file_stream=BytesIO(b"fake file"),
            file_name="curriculo.pdf",
            file_size_bytes=None,
        )

        with pytest.raises(
            DomainException,
            match="dados do arquivo do currículo são obrigatórios",
        ):
            use_case.execute(request)

        parser_service.parse.assert_not_called()
        analysis_provider.analyze.assert_not_called()
        job_repository.add.assert_not_called()
        analysis_repository.add.assert_not_called()
