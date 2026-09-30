from typing import Any

from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult
from MatchCV.Application.DTOs.AnalyzeResumeRequest import (
    AnalyzeResumeRequest,
)
from MatchCV.Application.Interfaces.IAnalysisProvider import (
    IAnalysisProvider,
)
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Domain.Entities.Resume import Resume
from MatchCV.Parser.Services.ResumeParserService import (
    ResumeParserService,
)


class AnalyzeResumeUseCase:
    """Orquestra o fluxo principal de análise de currículo."""

    def __init__(
        self,
        resume_parser_service: ResumeParserService,
        analysis_provider: IAnalysisProvider,
    ) -> None:
        self._resume_parser_service = resume_parser_service
        self._analysis_provider = analysis_provider

    def execute(
        self,
        request: AnalyzeResumeRequest,
    ) -> AnalysisResult:
        job_description = JobDescription.create(
            request.job_description
        )

        parsed_resume = self._resume_parser_service.parse(
            file_stream=request.file_stream,
            file_name=request.file_name,
            file_size_bytes=request.file_size_bytes,
        )

        resume = Resume.create(
            file_name=parsed_resume.file_name,
            file_type=parsed_resume.file_type,
            file_size_bytes=parsed_resume.file_size_bytes,
            page_count=parsed_resume.page_count,
            extracted_text=parsed_resume.extracted_text,
        )

        analysis = Analysis.create(
            resume_id=resume.id,
            job_description_id=job_description.id,
        )

        analysis.start_processing()

        result = self._analysis_provider.analyze(
            resume_text=resume.extracted_text,
            job_description=job_description.content,
        )

        analysis.complete(
            evidenced_requirements=result.get(
                "evidenced_requirements",
                [],
            ),
            unevidenced_requirements=result.get(
                "unevidenced_requirements",
                [],
            ),
            gaps=result.get(
                "gaps",
                [],
            ),
            resume_issues=result.get(
                "resume_issues",
                [],
            ),
            suggestions=result.get(
                "suggestions",
                [],
            ),
        )

        return AnalysisResult(
            evidenced_requirements=analysis.evidenced_requirements,
            unevidenced_requirements=analysis.unevidenced_requirements,
            gaps=analysis.gaps,
            resume_issues=analysis.resume_issues,
            suggestions=analysis.suggestions,
        )
