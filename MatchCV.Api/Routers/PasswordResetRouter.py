import hashlib
import os
import secrets
from typing import Annotated
from urllib.parse import quote

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
from MatchCV.Infrastructure.Services.PasswordResetEmailSender import (
    PasswordResetEmailSender,
)


router = APIRouter(prefix="/auth/password-reset", tags=["Password recovery"])


def get_password_reset_repository() -> SqlServerPasswordResetRepository:
    return SqlServerPasswordResetRepository(
        database_connection=get_database_connection(),
    )


def get_password_reset_email_sender() -> PasswordResetEmailSender:
    return PasswordResetEmailSender()


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
    email_sender: Annotated[
        PasswordResetEmailSender,
        Depends(get_password_reset_email_sender),
    ],
) -> PasswordResetRequestResponse:
    email = request.email.strip().lower()

    # Resposta uniforme: não confirma se a conta existe, nem se é ADMIN.
    message = (
        "Se houver uma conta elegível para esse e-mail, "
        "você receberá instruções de recuperação."
    )

    if "@" in email and not email.startswith("@"):
        digest: str | None = None
        created = False
        candidate = secrets.token_urlsafe(32)
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        try:
            created = repository.create_token(email, digest)
            if created:
                environment = os.getenv("APP_ENVIRONMENT", "development").strip().lower()
                if environment in {"production", "prod"} and os.getenv(
                    "MATCHCV_PASSWORD_RESET_EXPOSE_TOKEN", ""
                ).strip().lower() == "true":
                    repository.revoke_token(digest)
                    raise RuntimeError(
                        "MATCHCV_PASSWORD_RESET_EXPOSE_TOKEN não pode ser habilitado em produção."
                    )

                frontend_url = os.getenv("PASSWORD_RESET_FRONTEND_URL", "").strip().rstrip("/")
                if not frontend_url:
                    repository.revoke_token(digest)
                    raise RuntimeError("PASSWORD_RESET_FRONTEND_URL não configurada.")

                reset_url = (
                    f"{frontend_url}/forgot-password#token={quote(candidate, safe='')}"
                )
                email_sender.send_recovery_instructions(email, reset_url)
        except Exception:
            # Revoga o token se não foi possível concluir o envio. Não expõe detalhes.
            import logging

            if created and digest:
                try:
                    repository.revoke_token(digest)
                except Exception:
                    logging.getLogger(__name__).exception(
                        "Não foi possível revogar token após falha no envio de recuperação."
                    )
            logging.getLogger(__name__).exception(
                "Falha ao processar solicitação de recuperação de senha."
            )

    return PasswordResetRequestResponse(message=message)


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
