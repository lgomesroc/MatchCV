from io import BytesIO
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from MatchCV.Api.Dependencies.AnalysisDependencies import (
    get_analyze_resume_use_case, get_database_connection,
)
from MatchCV.Api.Schemas.AnalysisResponse import AnalysisResponse
from MatchCV.Api.Schemas.ErrorResponse import ErrorResponse
from MatchCV.Application.DTOs.AnalyzeResumeRequest import AnalyzeResumeRequest
from MatchCV.Application.UseCases.AnalyzeResumeUseCase import AnalyzeResumeUseCase
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisRepository import SqlServerAnalysisRepository
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisUsageRepository import (
    MonthlyQuotaExceeded,
    SqlServerAnalysisUsageRepository,
)
from MatchCV.Login.Authorization.CurrentUser import get_current_user


router = APIRouter(prefix="/analysis", tags=["Analysis"])


def get_analysis_usage_repository() -> SqlServerAnalysisUsageRepository:
    return SqlServerAnalysisUsageRepository(get_database_connection())


def get_analysis_repository() -> SqlServerAnalysisRepository:
    return SqlServerAnalysisRepository(get_database_connection())


@router.post(
    "/resume",
    response_model=AnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def analyze_resume(
    job_description: Annotated[str, Form(...)],
    use_case: Annotated[AnalyzeResumeUseCase, Depends(get_analyze_resume_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
    usage_repository: Annotated[SqlServerAnalysisUsageRepository, Depends(get_analysis_usage_repository)],
    resume_text: Annotated[str | None, Form()] = None,
    resume: Annotated[UploadFile | None, File()] = None,
) -> AnalysisResponse:
    has_resume_text = bool(resume_text and resume_text.strip())
    has_resume_file = resume is not None
    if has_resume_text and has_resume_file:
        raise HTTPException(status_code=400, detail="Informe o currículo por texto ou por arquivo, não pelos dois.")
    if not has_resume_text and not has_resume_file:
        raise HTTPException(status_code=400, detail="Cole o currículo ou escolha um arquivo antes de continuar.")

    if has_resume_text:
        request = AnalyzeResumeRequest(job_description=job_description, resume_text=resume_text)
    else:
        if not resume.filename:
            raise HTTPException(status_code=400, detail="O arquivo do currículo não possui nome.")
        file_content = await resume.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="O arquivo do currículo está vazio.")
        request = AnalyzeResumeRequest(
            job_description=job_description,
            file_stream=BytesIO(file_content),
            file_name=resume.filename,
            file_size_bytes=len(file_content),
        )

    reservation_id = None
    if current_user.role != UserRole.ADMIN:
        try:
            reservation_id = usage_repository.reserve_monthly_slot(current_user.id)
        except MonthlyQuotaExceeded as exception:
            raise HTTPException(status_code=403, detail=str(exception)) from exception

    try:
        analysis = use_case.enqueue(request, user_id=current_user.id)
        if reservation_id is not None:
            usage_repository.link_analysis(reservation_id, analysis.id)
        return AnalysisResponse(analysis_id=analysis.id, status=analysis.status.value)
    except DomainException as exception:
        if reservation_id is not None:
            usage_repository.release_reservation(reservation_id)
        raise HTTPException(status_code=400, detail=str(exception)) from exception
    except NotImplementedError as exception:
        if reservation_id is not None:
            usage_repository.release_reservation(reservation_id)
        raise HTTPException(status_code=503, detail=str(exception)) from exception
    except HTTPException:
        if reservation_id is not None:
            usage_repository.release_reservation(reservation_id)
        raise
    except Exception as exception:
        if reservation_id is not None:
            usage_repository.release_reservation(reservation_id)
        raise HTTPException(
            status_code=500,
            detail="Não foi possível colocar a análise na fila.",
        ) from exception


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_status(
    analysis_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[SqlServerAnalysisRepository, Depends(get_analysis_repository)],
) -> AnalysisResponse:
    analysis = repository.get_by_id_and_user(analysis_id, current_user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return AnalysisResponse(
        analysis_id=analysis.id,
        status=analysis.status.value.lower(),
        evidenced_requirements=analysis.evidenced_requirements,
        unevidenced_requirements=analysis.unevidenced_requirements,
        gaps=analysis.gaps,
        resume_issues=analysis.resume_issues,
        suggestions=analysis.suggestions,
    )
