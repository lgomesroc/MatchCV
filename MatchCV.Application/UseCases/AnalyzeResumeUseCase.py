from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult
from MatchCV.Application.DTOs.AnalyzeResumeRequest import AnalyzeResumeRequest
from MatchCV.Application.Interfaces.IAnalysisProvider import IAnalysisProvider
from MatchCV.Application.Interfaces.IResumeParserService import IResumeParserService
from MatchCV.Application.Repositories.IAnalysisRepository import IAnalysisRepository
from MatchCV.Application.Repositories.IJobDescriptionRepository import (
    IJobDescriptionRepository,
)
from MatchCV.Domain.Entities.Analysis import Analysis
from MatchCV.Domain.Entities.JobDescription import JobDescription
from MatchCV.Domain.Entities.Resume import Resume


class AnalyzeResumeUseCase:
    """
    Caso de uso responsável por processar um currículo e realizar
    a análise em relação a uma descrição de vaga.

    A Application depende apenas de abstrações próprias.
    Implementações concretas de Parser, IA e persistência ficam
    fora desta camada.
    """

    def __init__(
        self,
        resume_parser_service: IResumeParserService,
        analysis_provider: IAnalysisProvider,
        job_description_repository: IJobDescriptionRepository,
        analysis_repository: IAnalysisRepository,
    ) -> None:
        self._resume_parser_service = resume_parser_service
        self._analysis_provider = analysis_provider
        self._job_description_repository = job_description_repository
        self._analysis_repository = analysis_repository

    def execute(
        self,
        request: AnalyzeResumeRequest,
    ) -> AnalysisResult:
        """
        Executa a análise do currículo.

        O fluxo é:

        1. Cria e valida a descrição da vaga.
        2. Processa e valida o currículo através da abstração do parser.
        3. Cria a entidade Resume.
        4. Persiste a descrição da vaga.
        5. Cria e inicia a análise.
        6. Executa a análise através da abstração de IA.
        7. Persiste o resultado da análise.
        8. Em caso de erro, marca a análise como falha.
        """

        job_description = JobDescription.create(
            request.job_description,
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

        self._job_description_repository.add(
            job_description,
        )

        analysis = Analysis.create(
            resume_id=resume.id,
            job_description_id=job_description.id,
        )

        self._analysis_repository.add(
            analysis,
        )

        analysis.start_processing()

        self._analysis_repository.update(
            analysis,
        )

        try:
            result = self._analysis_provider.analyze(
                resume_text=resume.extracted_text,
                job_description=job_description.content,
            )

            analysis.complete(
                evidenced_requirements=result.evidenced_requirements,
                unevidenced_requirements=result.unevidenced_requirements,
                gaps=result.gaps,
                resume_issues=result.resume_issues,
                suggestions=result.suggestions,
            )

            self._analysis_repository.update(
                analysis,
            )

            return result

        except Exception:
            analysis.fail()

            self._analysis_repository.update(
                analysis,
            )

            raise
