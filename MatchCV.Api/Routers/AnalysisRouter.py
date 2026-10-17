
from io import BytesIO
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from MatchCV.Api.Dependencies.AnalysisDependencies import (
    get_analyze_resume_use_case,
    get_database_connection,
)
from MatchCV.Api.Schemas.AnalysisResponse import AnalysisResponse
from MatchCV.Api.Schemas.ErrorResponse import ErrorResponse
from MatchCV.Application.DTOs.AnalyzeResumeRequest import (
    AnalyzeResumeRequest,
)
from MatchCV.Application.UseCases.AnalyzeResumeUseCase import (
    AnalyzeResumeUseCase,
)
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Infrastructure.Repositories.SqlServerAnalysisUsageRepository import (
    SqlServerAnalysisUsageRepository,
)
from MatchCV.Login.Authorization.CurrentUser import get_current_user


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


def get_analysis_usage_repository() -> SqlServerAnalysisUsageRepository:
    return SqlServerAnalysisUsageRepository(
        database_connection=get_database_connection(),
    )


@router.post(
    "/resume",
    response_model=AnalysisResponse,
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
    use_case: Annotated[
        AnalyzeResumeUseCase,
        Depends(get_analyze_resume_use_case),
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    usage_repository: Annotated[
        SqlServerAnalysisUsageRepository,
        Depends(get_analysis_usage_repository),
    ],
    resume_text: Annotated[str | None, Form()] = None,
    resume: Annotated[UploadFile | None, File()] = None,
) -> AnalysisResponse:
    if current_user.role != UserRole.ADMIN:
        completed_count = usage_repository.count_completed(current_user.id)

        if completed_count >= usage_repository.FREE_ANALYSIS_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Você atingiu o limite de três análises concluídas "
                    "da versão gratuita."
                ),
            )

    has_resume_text = bool(resume_text and resume_text.strip())
    has_resume_file = resume is not None

    if has_resume_text and has_resume_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Informe o currículo por texto ou por arquivo, "
                "não pelos dois."
            ),
        )

    if not has_resume_text and not has_resume_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cole o currículo ou escolha um arquivo "
                "antes de continuar."
            ),
        )

    if has_resume_text:
        request = AnalyzeResumeRequest(
            job_description=job_description,
            resume_text=resume_text,
        )
    else:
        if not resume.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo do currículo não possui nome.",
            )

        file_content = await resume.read()

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo do currículo está vazio.",
            )

        request = AnalyzeResumeRequest(
            job_description=job_description,
            file_stream=BytesIO(file_content),
            file_name=resume.filename,
            file_size_bytes=len(file_content),
        )

    try:
        result = use_case.execute(
            request,
            user_id=current_user.id,
        )

        # Só contabiliza quando o caso de uso retorna com sucesso.
        if current_user.role != UserRole.ADMIN:
            usage_repository.record_success(current_user.id)

        return AnalysisResponse(
            status="completed",
            evidenced_requirements=result.evidenced_requirements,
            unevidenced_requirements=result.unevidenced_requirements,
            gaps=result.gaps,
            resume_issues=result.resume_issues,
            suggestions=result.suggestions,
        )

    except DomainException as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    except NotImplementedError as exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exception),
        ) from exception

    except HTTPException:
        raise

    except Exception as exception:
        print(
            f"[MatchCV] Erro ao processar análise: "
            f"{type(exception).__name__}: {exception}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível concluir a análise.",
        ) from exception
