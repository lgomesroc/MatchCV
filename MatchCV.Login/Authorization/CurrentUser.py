from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from MatchCV.Application.Repositories.IUserRepository import IUserRepository
from MatchCV.Domain.Entities.User import User
from MatchCV.Login.Dependencies.AuthDependencies import (
    get_token_service,
    get_user_repository,
)
from MatchCV.Login.Tokens.TokenService import TokenService

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    token_service: TokenService = Depends(get_token_service),
    user_repository: IUserRepository = Depends(get_user_repository),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticação necessária ou token inválido.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        payload = token_service.decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError) as exception:
        raise unauthorized from exception

    user = user_repository.get_by_id(user_id)
    if user is None:
        raise unauthorized

    token_password_version = payload.get("pwdv")
    current_password_version = token_service.password_version(user.password_hash)
    if (
        not isinstance(token_password_version, str)
        or not hmac_compare(token_password_version, current_password_version)
    ):
        raise unauthorized

    return user


def hmac_compare(left: str, right: str) -> bool:
    import hmac
    return hmac.compare_digest(left, right)
