
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from MatchCV.Login.Authorization.CurrentUser import get_current_user


class FakeTokenService:
    """Simula a validacao e a leitura de um token de acesso."""

    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def decode_access_token(self, token: str) -> dict:
        if self.error is not None:
            raise self.error

        return self.payload

    @staticmethod
    def password_version(password_hash: str) -> str:
        return f"version:{password_hash}"


class FakeUserRepository:
    """Repositorio em memoria para os testes de autorizacao."""

    def __init__(self, user=None):
        self.user = user
        self.requested_user_id = None

    def get_by_id(self, user_id):
        self.requested_user_id = user_id

        if self.user is None or self.user.id != user_id:
            return None

        return self.user


@pytest.fixture
def user():
    return SimpleNamespace(
        id=uuid4(),
        password_hash="hash-da-senha",
        name="Usuario de Teste",
        email="usuario@example.com",
    )


@pytest.fixture
def valid_payload(user):
    return {
        "sub": str(user.id),
        "exp": 9999999999,
        "pwdv": "version:hash-da-senha",
    }


@pytest.fixture
def credentials():
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token-de-teste",
    )


def test_rejects_request_without_credentials():
    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=None,
            token_service=FakeTokenService(),
            user_repository=FakeUserRepository(),
        )

    assert exception.value.status_code == 401
    assert exception.value.headers["WWW-Authenticate"] == "Bearer"


def test_rejects_invalid_token(credentials):
    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(
                error=ValueError("Token invalido.")
            ),
            user_repository=FakeUserRepository(),
        )

    assert exception.value.status_code == 401


def test_rejects_token_without_user_id(credentials):
    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(payload={}),
            user_repository=FakeUserRepository(),
        )

    assert exception.value.status_code == 401


def test_rejects_invalid_user_id(credentials):
    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(
                payload={
                    "sub": "id-invalido",
                    "pwdv": "version:hash-da-senha",
                }
            ),
            user_repository=FakeUserRepository(),
        )

    assert exception.value.status_code == 401


def test_rejects_token_when_user_does_not_exist(
    credentials,
    valid_payload,
):
    repository = FakeUserRepository()

    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(payload=valid_payload),
            user_repository=repository,
        )

    assert exception.value.status_code == 401


def test_rejects_token_without_password_version(
    credentials,
    valid_payload,
    user,
):
    payload = valid_payload.copy()
    payload.pop("pwdv")

    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(payload=payload),
            user_repository=FakeUserRepository(user),
        )

    assert exception.value.status_code == 401


def test_rejects_token_when_password_version_differs(
    credentials,
    valid_payload,
    user,
):
    payload = valid_payload.copy()
    payload["pwdv"] = "versao-de-senha-antiga"

    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(payload=payload),
            user_repository=FakeUserRepository(user),
        )

    assert exception.value.status_code == 401


def test_rejects_non_string_password_version(
    credentials,
    valid_payload,
    user,
):
    payload = valid_payload.copy()
    payload["pwdv"] = 12345

    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(payload=payload),
            user_repository=FakeUserRepository(user),
        )

    assert exception.value.status_code == 401


def test_returns_user_when_token_and_password_version_are_valid(
    credentials,
    valid_payload,
    user,
):
    repository = FakeUserRepository(user)

    result = get_current_user(
        credentials=credentials,
        token_service=FakeTokenService(payload=valid_payload),
        user_repository=repository,
    )

    assert result is user
    assert repository.requested_user_id == user.id


def test_rejects_old_token_after_password_change(
    credentials,
    valid_payload,
    user,
):
    payload = valid_payload.copy()

    # Simula a troca da senha no repositorio.
    user.password_hash = "novo-hash-da-senha"

    with pytest.raises(HTTPException) as exception:
        get_current_user(
            credentials=credentials,
            token_service=FakeTokenService(payload=payload),
            user_repository=FakeUserRepository(user),
        )

    assert exception.value.status_code == 401
