
from uuid import UUID

import pytest

from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Exceptions.DomainException import DomainException
from MatchCV.Login.Authentication.AuthenticationService import (
    AuthenticationService,
)
from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher


USER_ID = UUID("12345678-1234-5678-1234-567812345678")
VALID_PASSWORD = "MatchCV123!"
NEW_PASSWORD = "NovaSenha456@"
USER_NAME = "Luciano Gomes"
USER_EMAIL = "luciano@example.com"


class FakeUserRepository:
    """Repositorio em memoria para testes unitarios."""

    def __init__(self):
        self.users_by_id = {}
        self.users_by_email = {}
        self.fail_password_update = False
        self.hide_user_after_password_update = False

    def add(self, user: User) -> User:
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        return user

    def get_by_id(self, user_id: UUID):
        return self.users_by_id.get(user_id)

    def get_by_email(self, email: str):
        return self.users_by_email.get(email)

    def update_password_hash(
        self,
        user_id: UUID,
        password_hash: str,
    ) -> bool:
        if self.fail_password_update:
            return False

        user = self.users_by_id.get(user_id)

        if user is None:
            return False

        user.password_hash = password_hash

        if self.hide_user_after_password_update:
            del self.users_by_id[user_id]
            self.users_by_email.pop(user.email, None)

        return True


class FakeTokenService:
    """Substitui a geracao real de tokens nos testes."""

    def __init__(self):
        self.last_subject = None
        self.last_password_hash = None

    def create_access_token(
        self,
        subject: str,
        password_hash: str | None = None,
    ) -> str:
        self.last_subject = subject
        self.last_password_hash = password_hash
        return f"fake-token-{subject}"


@pytest.fixture
def repository():
    return FakeUserRepository()


@pytest.fixture
def token_service():
    return FakeTokenService()


@pytest.fixture
def auth_service(repository, token_service):
    return AuthenticationService(repository, token_service)


@pytest.fixture
def existing_user(repository):
    user = User.create(
        name=USER_NAME,
        email=USER_EMAIL,
        password_hash=PasswordHasher.hash_password(VALID_PASSWORD),
    )
    repository.add(user)
    return user


# Cadastro


def test_register_creates_user_with_normalized_email(auth_service):
    user = auth_service.register(
        name=USER_NAME,
        email="  LUCIANO@EXAMPLE.COM  ",
        password=VALID_PASSWORD,
    )

    assert user.name == USER_NAME
    assert user.email == USER_EMAIL
    assert user.password_hash != VALID_PASSWORD
    assert PasswordHasher.verify_password(
        VALID_PASSWORD,
        user.password_hash,
    )


def test_register_rejects_invalid_email(auth_service):
    with pytest.raises(DomainException, match="e-mail"):
        auth_service.register(
            name=USER_NAME,
            email="email-invalido",
            password=VALID_PASSWORD,
        )


def test_register_rejects_weak_password(auth_service):
    with pytest.raises(DomainException):
        auth_service.register(
            name=USER_NAME,
            email=USER_EMAIL,
            password="fraca",
        )


def test_register_rejects_duplicate_email(
    auth_service,
    existing_user,
):
    with pytest.raises(DomainException, match="Já existe"):
        auth_service.register(
            name=USER_NAME,
            email=existing_user.email.upper(),
            password=VALID_PASSWORD,
        )


# Login


def test_authenticate_returns_user_with_valid_credentials(
    auth_service,
    existing_user,
):
    authenticated_user = auth_service.authenticate(
        USER_EMAIL.upper(),
        VALID_PASSWORD,
    )

    assert authenticated_user.id == existing_user.id
    assert authenticated_user.email == USER_EMAIL


def test_authenticate_rejects_incorrect_password(
    auth_service,
    existing_user,
):
    with pytest.raises(ValueError, match="inválidos"):
        auth_service.authenticate(
            USER_EMAIL,
            "SenhaErrada123!",
        )


def test_authenticate_rejects_nonexistent_user(auth_service):
    with pytest.raises(ValueError, match="inválidos"):
        auth_service.authenticate(
            "inexistente@example.com",
            VALID_PASSWORD,
        )


# Troca de senha


def test_change_password_updates_hash_and_returns_updated_user(
    auth_service,
    repository,
    existing_user,
):
    original_hash = existing_user.password_hash

    updated_user = auth_service.change_password(
        user_id=existing_user.id,
        current_password=VALID_PASSWORD,
        new_password=NEW_PASSWORD,
    )

    assert updated_user.id == existing_user.id
    assert updated_user.password_hash != original_hash
    assert updated_user.password_hash != NEW_PASSWORD
    assert PasswordHasher.verify_password(
        NEW_PASSWORD,
        updated_user.password_hash,
    )
    assert not PasswordHasher.verify_password(
        VALID_PASSWORD,
        updated_user.password_hash,
    )
    assert repository.get_by_id(existing_user.id) is updated_user


def test_change_password_rejects_nonexistent_user(auth_service):
    with pytest.raises(ValueError, match="não encontrado"):
        auth_service.change_password(
            user_id=USER_ID,
            current_password=VALID_PASSWORD,
            new_password=NEW_PASSWORD,
        )


def test_change_password_rejects_incorrect_current_password(
    auth_service,
    existing_user,
):
    original_hash = existing_user.password_hash

    with pytest.raises(ValueError, match="incorreta"):
        auth_service.change_password(
            user_id=existing_user.id,
            current_password="SenhaErrada123!",
            new_password=NEW_PASSWORD,
        )

    assert existing_user.password_hash == original_hash


def test_change_password_rejects_weak_new_password(
    auth_service,
    existing_user,
):
    original_hash = existing_user.password_hash

    with pytest.raises(DomainException):
        auth_service.change_password(
            user_id=existing_user.id,
            current_password=VALID_PASSWORD,
            new_password="fraca",
        )

    assert existing_user.password_hash == original_hash


def test_change_password_rejects_same_password(
    auth_service,
    existing_user,
):
    original_hash = existing_user.password_hash

    with pytest.raises(DomainException, match="diferente"):
        auth_service.change_password(
            user_id=existing_user.id,
            current_password=VALID_PASSWORD,
            new_password=VALID_PASSWORD,
        )

    assert existing_user.password_hash == original_hash


def test_change_password_reports_repository_update_failure(
    auth_service,
    repository,
    existing_user,
):
    original_hash = existing_user.password_hash
    repository.fail_password_update = True

    with pytest.raises(ValueError, match="atualizar a senha"):
        auth_service.change_password(
            user_id=existing_user.id,
            current_password=VALID_PASSWORD,
            new_password=NEW_PASSWORD,
        )

    assert existing_user.password_hash == original_hash


def test_change_password_reports_missing_user_after_update(
    auth_service,
    repository,
    existing_user,
):
    repository.hide_user_after_password_update = True

    with pytest.raises(ValueError, match="carregar a conta"):
        auth_service.change_password(
            user_id=existing_user.id,
            current_password=VALID_PASSWORD,
            new_password=NEW_PASSWORD,
        )


# Geracao de token


def test_create_access_token_uses_user_id_and_password_hash(
    auth_service,
    token_service,
    existing_user,
):
    token = auth_service.create_access_token(existing_user)

    assert token == f"fake-token-{existing_user.id}"
    assert token_service.last_subject == str(existing_user.id)
    assert token_service.last_password_hash == existing_user.password_hash


def test_create_access_token_uses_updated_password_hash(
    auth_service,
    token_service,
    existing_user,
):
    updated_user = auth_service.change_password(
        user_id=existing_user.id,
        current_password=VALID_PASSWORD,
        new_password=NEW_PASSWORD,
    )

    token = auth_service.create_access_token(updated_user)

    assert token == f"fake-token-{existing_user.id}"
    assert token_service.last_password_hash == updated_user.password_hash
    assert PasswordHasher.verify_password(
        NEW_PASSWORD,
        token_service.last_password_hash,
    )
