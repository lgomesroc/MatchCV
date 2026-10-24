import hashlib
import os
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from MatchCV.Api.Dependencies.AnalysisDependencies import get_database_connection
from MatchCV.Api.Schemas.AuthSchemas import (
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
)
from MatchCV.Infrastructure.Repositories.SqlServerPasswordResetRepository import (
    SqlServerPasswordResetRepository,
)
from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher
from MatchCV.Login.Authentication.PasswordPolicy import PasswordPolicy


router = APIRouter(prefix="/auth/password-reset", tags=["Password recovery"])


def get_password_reset_repository() -> SqlServerPasswordResetRepository:
    return SqlServerPasswordResetRepository(
        database_connection=get_database_connection(),
    )


@router.post(
    "/request",
    response_model=PasswordResetRequestResponse,
    response_model_exclude_none=True,
)
def request_password_reset(
    request: PasswordResetRequest,
    repository: Annotated[
        SqlServerPasswordResetRepository,
        Depends(get_password_reset_repository),
    ],
) -> PasswordResetRequestResponse:
    email = request.email.strip().lower()
    reset_token: str | None = None

    # Resposta uniforme: não confirma se a conta existe nem se é ADMIN.
    if "@" in email and not email.startswith("@"):
        candidate = secrets.token_urlsafe(32)
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        created = repository.create_token(email, digest)

        if created:
            environment = os.getenv("APP_ENVIRONMENT", "development").lower()
            expose_token = (
                environment == "development"
                and os.getenv("MATCHCV_PASSWORD_RESET_EXPOSE_TOKEN", "").lower()
                == "true"
            )
            if expose_token:
                reset_token = candidate

    return PasswordResetRequestResponse(
        message=(
            "Se a conta puder recuperar a senha, as instruções serão "
            "disponibilizadas pelo canal de recuperação configurado."
        ),
        reset_token=reset_token,
    )


@router.post("/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    repository: Annotated[
        SqlServerPasswordResetRepository,
        Depends(get_password_reset_repository),
    ],
) -> None:
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A confirmação não corresponde à nova senha.",
        )

    try:
        PasswordPolicy.validate(request.new_password)
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exception),
        ) from exception

    token_hash = hashlib.sha256(request.token.encode("utf-8")).hexdigest()
    password_hash = PasswordHasher.hash_password(request.new_password)

    if not repository.consume_token(token_hash, password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido, expirado ou já utilizado.",
        )
