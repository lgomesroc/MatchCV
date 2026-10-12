from fastapi import Depends, HTTPException, status

from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Login.Authorization.CurrentUser import get_current_user


def require_role(*allowed_roles: UserRole):
    """Cria uma dependência que exige uma das funções informadas."""

    def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para executar esta operação.",
            )

        return current_user

    return check_role
