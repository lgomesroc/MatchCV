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
)
from MatchCV.Api.Schemas.AnalysisResponse import AnalysisResponse
from MatchCV.Api.Schemas.ErrorResponse import ErrorResponse
from MatchCV.Application.DTOs.AnalyzeResumeRequest import (
    AnalyzeResumeRequest,
)
from MatchCV.Application.UseCases.AnalyzeResumeUseCase import (
    AnalyzeResumeUseCase,
)
from MatchCV.Domain.Exceptions.DomainException import DomainException


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.post(
    "/resume",
    response_model=AnalysisResponse,
    responses={
        400: {
            "model": ErrorResponse,
        },
        500: {
            "model": ErrorResponse,
        },
        503: {
            "model": ErrorResponse,
        },
    },
)
async def analyze_resume(
    job_description: Annotated[
        str,
        Form(...),
    ],
    resume_text: Annotated[
        str | None,
        Form(None),
    ],
    resume: Annotated[
        UploadFile | None,
        File(None),
    ],
    use_case: Annotated[
        AnalyzeResumeUseCase,
        Depends(get_analyze_resume_use_case),
    ],
) -> AnalysisResponse:
    has_resume_text = bool(
        resume_text and resume_text.strip()
    )

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
        result = use_case.execute(request)

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

    except Exception as exception:
        print(
            f"[MatchCV] Erro ao processar análise: "
            f"{type(exception).__name__}: {exception}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exception),
        ) from exception
