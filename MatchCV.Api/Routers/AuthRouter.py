
import hmac
import os
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from MatchCV.Api.Schemas.AuthSchemas import (
    AdminBootstrapRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Infrastructure.Repositories.SqlServerUserRepository import (
    SqlServerUserRepository,
)
from MatchCV.Login.Authentication.AuthenticationService import (
    AuthenticationService,
)
from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher
from MatchCV.Login.Authentication.PasswordPolicy import PasswordPolicy
from MatchCV.Login.Authorization.CurrentUser import get_current_user
from MatchCV.Login.Dependencies.AuthDependencies import (
    get_authentication_service,
    get_user_repository,
)


from MatchCV.Api.Schemas.AuthSchemas import ChangePasswordRequest


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    auth_service: Annotated[
        AuthenticationService,
        Depends(get_authentication_service),
    ],
) -> UserResponse:
    try:
        user = auth_service.register(
            name=request.name,
            email=request.email,
            password=request.password,
        )
    except DomainException as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: Annotated[
        AuthenticationService,
        Depends(get_authentication_service),
    ],
) -> TokenResponse:
    try:
        user = auth_service.authenticate(
            email=request.email,
            password=request.password,
        )
        access_token = auth_service.create_access_token(user)
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exception

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
        ),
    )


@router.post(
    "/admin/bootstrap",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def bootstrap_admin(
    request: AdminBootstrapRequest,
    repository: Annotated[
        SqlServerUserRepository,
        Depends(get_user_repository),
    ],
    bootstrap_token: Annotated[
        str | None,
        Header(alias="X-Admin-Bootstrap-Token"),
    ] = None,
) -> UserResponse:
    configured_token = os.getenv("MATCHCV_ADMIN_BOOTSTRAP_TOKEN", "")

    if len(configured_token) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A inicialização administrativa não está configurada.",
        )

    if not bootstrap_token or not hmac.compare_digest(
        bootstrap_token,
        configured_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de inicialização inválido.",
        )

    email = request.email.strip().lower()

    if email != "admin@admin.com":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O administrador inicial deve usar admin@admin.com.",
        )

    try:
        PasswordPolicy.validate(request.password)
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exception),
        ) from exception

    if "@" not in email or email.startswith("@"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe um e-mail válido.",
        )

    try:
        password_hash = PasswordHasher.hash_password(request.password)
        user = User.create(
            name=request.name,
            email=email,
            password_hash=password_hash,
            role=UserRole.ADMIN,
        )
        repository.add_admin_if_none_exists(user)
    except DomainException as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exception),
        ) from exception
    except Exception as exception:
        # A restrição única do banco também protege contra concorrência.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Não foi possível criar o administrador. "
                "Verifique se já existe um administrador e se o e-mail está livre."
            ),
        ) from exception

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: Annotated[
        AuthenticationService, Depends(get_authentication_service)
    ],
) -> None:
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A confirmação não corresponde à nova senha.",
        )

    try:
        auth_service.change_password(
            user_id=current_user.id,
            current_password=request.current_password,
            new_password=request.new_password,
        )
    except DomainException as exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exception),
        ) from exception
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception),
        ) from exception
