from functools import lru_cache

from MatchCV.Application.Repositories.IUserRepository import IUserRepository
from MatchCV.Infrastructure.Repositories.SqlServerUserRepository import (
    SqlServerUserRepository,
)
from MatchCV.Login.Authentication.AuthenticationService import (
    AuthenticationService,
)
from MatchCV.Login.Tokens.TokenService import TokenService

from MatchCV.Api.Dependencies.AnalysisDependencies import (
    get_database_connection,
)


@lru_cache
def get_token_service() -> TokenService:
    return TokenService()


def get_user_repository() -> IUserRepository:
    return SqlServerUserRepository(
        database_connection=get_database_connection(),
    )


def get_authentication_service() -> AuthenticationService:
    return AuthenticationService(
        user_repository=get_user_repository(),
        token_service=get_token_service(),
    )
