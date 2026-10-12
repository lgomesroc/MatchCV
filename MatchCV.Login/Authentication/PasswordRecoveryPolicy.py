from MatchCV.Domain.Enums.UserRole import UserRole


class PasswordRecoveryPolicy:
    """Define quais funções podem usar a recuperação pública de senha."""

    @staticmethod
    def can_use_public_recovery(role: UserRole) -> bool:
        return role != UserRole.ADMIN
