from functools import lru_cache

from MatchCV.AI.Providers.OpenAICompatibleProvider import (
    OpenAICompatibleProvider,
)
from MatchCV.AI.Providers.SecondaryAIProvider import SecondaryAIProvider
from MatchCV.AI.Services.AIProviderService import AIProviderService
from MatchCV.Application.UseCases.AnalyzeResumeUseCase import AnalyzeResumeUseCase
from MatchCV.Infrastructure.Config.AISettings import AISettings
from MatchCV.Infrastructure.Config.AppSettings import AppSettings
from MatchCV.Infrastructure.Database.DatabaseConnection import DatabaseConnection
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisRepository import (
    SqlServerAnalysisRepository,
)
from MatchCV.Infrastructure.Repositories.SqlServerJobDescriptionRepository import (
    SqlServerJobDescriptionRepository,
)
from MatchCV.Infrastructure.Services.AIAnalysisProvider import AIAnalysisProvider
from MatchCV.Infrastructure.Services.ResumeParserAdapter import ResumeParserAdapter
from MatchCV.Parser.Parsers.DocResumeParser import DocResumeParser
from MatchCV.Parser.Parsers.DocxResumeParser import DocxResumeParser
from MatchCV.Parser.Parsers.PdfResumeParser import PdfResumeParser
from MatchCV.Parser.Services.ResumeParserService import ResumeParserService


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings.from_environment()


@lru_cache
def get_database_connection() -> DatabaseConnection:
    return DatabaseConnection(
        settings=get_app_settings(),
    )


def get_analyze_resume_use_case() -> AnalyzeResumeUseCase:
    settings = get_app_settings()

    pdf_parser = PdfResumeParser()
    doc_parser = DocResumeParser()
    docx_parser = DocxResumeParser()

    parser_service = ResumeParserService(
        pdf_parser=pdf_parser,
        doc_parser=doc_parser,
        docx_parser=docx_parser,
    )

    resume_parser_adapter = ResumeParserAdapter(
        parser_service=parser_service,
    )

    primary_provider = OpenAICompatibleProvider(
        config=AISettings.primary(settings),
    )

    fallback_provider = SecondaryAIProvider(
        config=AISettings.fallback(settings),
    )

    ai_provider_service = AIProviderService(
        primary_provider=primary_provider,
        fallback_provider=fallback_provider,
    )

    ai_analysis_provider = AIAnalysisProvider(
        ai_provider_service=ai_provider_service,
    )

    database_connection = get_database_connection()

    job_description_repository = SqlServerJobDescriptionRepository(
        database_connection=database_connection,
    )

    analysis_repository = SqlServerAnalysisRepository(
        database_connection=database_connection,
    )

    return AnalyzeResumeUseCase(
        resume_parser_service=resume_parser_adapter,
        analysis_provider=ai_analysis_provider,
        job_description_repository=job_description_repository,
        analysis_repository=analysis_repository,
    )
