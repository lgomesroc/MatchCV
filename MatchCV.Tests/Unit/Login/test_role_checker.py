
import pytest
from fastapi import HTTPException

from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Login.Authorization.RoleChecker import require_role


@pytest.fixture
def regular_user():
    return User.create(
        name="Usuario Comum",
        email="usuario@example.com",
        password_hash="hash-de-teste",
        role=UserRole.USER,
    )


@pytest.fixture
def admin_user():
    return User.create(
        name="Administrador",
        email="admin@example.com",
        password_hash="hash-de-teste",
        role=UserRole.ADMIN,
    )


def test_allows_user_when_role_is_permitted(regular_user):
    checker = require_role(UserRole.USER)

    result = checker(current_user=regular_user)

    assert result is regular_user


def test_allows_admin_when_role_is_permitted(admin_user):
    checker = require_role(UserRole.ADMIN)

    result = checker(current_user=admin_user)

    assert result is admin_user


def test_rejects_user_when_admin_role_is_required(regular_user):
    checker = require_role(UserRole.ADMIN)

    with pytest.raises(HTTPException) as error:
        checker(current_user=regular_user)

    assert error.value.status_code == 403


def test_rejects_admin_when_only_user_role_is_permitted(admin_user):
    checker = require_role(UserRole.USER)

    with pytest.raises(HTTPException) as error:
        checker(current_user=admin_user)

    assert error.value.status_code == 403


def test_allows_any_role_in_explicit_allowlist(admin_user):
    checker = require_role(UserRole.USER, UserRole.ADMIN)

    result = checker(current_user=admin_user)

    assert result is admin_user


def test_rejects_all_roles_when_allowlist_is_empty(regular_user):
    checker = require_role()

    with pytest.raises(HTTPException) as error:
        checker(current_user=regular_user)

    assert error.value.status_code == 403
