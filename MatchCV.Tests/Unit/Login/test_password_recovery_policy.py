from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Login.Authentication.PasswordRecoveryPolicy import (
    PasswordRecoveryPolicy,
)


def test_admin_cannot_use_public_password_recovery() -> None:
    assert PasswordRecoveryPolicy.can_use_public_recovery(
        UserRole.ADMIN
    ) is False


def test_regular_user_can_use_public_password_recovery_policy() -> None:
    assert PasswordRecoveryPolicy.can_use_public_recovery(
        UserRole.USER
    ) is True
