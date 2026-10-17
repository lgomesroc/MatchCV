
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from MatchCV.Api.main import app
from MatchCV.Domain.Entities.User import User
from MatchCV.Domain.Enums.UserRole import UserRole
from MatchCV.Infrastructure.Repositories.SqlServerUserRepository import (
    SqlServerUserRepository,
)
from MatchCV.Login.Authentication.AuthenticationService import (
    AuthenticationService,
)
from MatchCV.Login.Dependencies.AuthDependencies import (
    get_authentication_service,
    get_token_service,
    get_user_repository,
)
from MatchCV.Login.Tokens.TokenService import TokenService


VALID_PASSWORD = "MatchCV123!"
NEW_PASSWORD = "NovaSenha456@"


class FakeUserRepository:
    """Repositorio em memoria para testes das rotas de autenticacao."""

    def __init__(self):
        self.users_by_id: dict[UUID, User] = {}
        self.users_by_email: dict[str, User] = {}

    def add(self, user: User) -> User:
        if user.email in self.users_by_email:
            raise ValueError("Ja existe uma conta com esse e-mail.")

        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        return user

    def get_by_id(self, user_id: UUID):
        return self.users_by_id.get(user_id)

    def get_by_email(self, email: str):
        return self.users_by_email.get(email.strip().lower())

    def update_password_hash(
        self,
        user_id: UUID,
        password_hash: str,
    ) -> bool:
        user = self.users_by_id.get(user_id)

        if user is None:
            return False

        user.password_hash = password_hash
        return True

    def add_admin_if_none_exists(self, user: User) -> User:
        if any(
            existing.role == UserRole.ADMIN
            for existing in self.users_by_id.values()
        ):
            raise ValueError("Ja existe um administrador.")

        if user.email in self.users_by_email:
            raise ValueError("Ja existe uma conta com esse e-mail.")

        return self.add(user)


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setenv(
        "MATCHCV_JWT_SECRET",
        "chave-de-teste-com-mais-de-32-bytes",
    )
    monkeypatch.setenv("MATCHCV_ACCESS_TOKEN_MINUTES", "30")

    token_service = TokenService()
    repository = FakeUserRepository()
    auth_service = AuthenticationService(repository, token_service)

    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[get_authentication_service] = (
        lambda: auth_service
    )
    app.dependency_overrides[get_user_repository] = (
        lambda: repository
    )
    app.dependency_overrides[get_token_service] = (
        lambda: token_service
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous_overrides)


@pytest.fixture
def registration_payload():
    return {
        "name": "Usuario de Teste",
        "email": "usuario@example.com",
        "password": VALID_PASSWORD,
    }


def register_user(client, payload=None):
    response = client.post(
        "/api/v1/auth/register",
        json=payload
        or {
            "name": "Usuario de Teste",
            "email": "usuario@example.com",
            "password": VALID_PASSWORD,
        },
    )
    return response


def login_user(client, email="usuario@example.com", password=VALID_PASSWORD):
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def register_and_login(client):
    registration = register_user(client)
    assert registration.status_code == 201

    login = login_user(client)
    assert login.status_code == 200

    return login.json()


# Cadastro


def test_register_returns_created_user_without_password_hash(
    api_client,
    registration_payload,
):
    response = register_user(api_client, registration_payload)

    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Usuario de Teste"
    assert body["email"] == "usuario@example.com"
    assert body["role"] == UserRole.USER.value
    assert "password" not in body
    assert "password_hash" not in body


def test_register_normalizes_email(api_client):
    response = register_user(
        api_client,
        {
            "name": "Usuario de Teste",
            "email": "  USUARIO@EXAMPLE.COM  ",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "usuario@example.com"


def test_register_rejects_duplicate_email(
    api_client,
    registration_payload,
):
    first_response = register_user(api_client, registration_payload)
    second_response = register_user(api_client, registration_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_register_rejects_invalid_request(api_client):
    response = api_client.post(
        "/api/v1/auth/register",
        json={
            "name": "A",
            "email": "email-invalido",
            "password": "123",
        },
    )

    assert response.status_code == 422


# Login


def test_login_returns_access_token_and_user(api_client):
    register_user(api_client)

    response = login_user(api_client)

    assert response.status_code == 200

    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "usuario@example.com"
    assert body["user"]["role"] == UserRole.USER.value


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("usuario@example.com", "SenhaErrada123!"),
        ("inexistente@example.com", VALID_PASSWORD),
    ],
)
def test_login_rejects_invalid_credentials(
    api_client,
    email,
    password,
):
    register_user(api_client)

    response = login_user(
        api_client,
        email=email,
        password=password,
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


# Usuario autenticado


def test_me_rejects_request_without_token(api_client):
    response = api_client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_authenticated_user(api_client):
    login = register_and_login(api_client)

    response = api_client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {login['access_token']}",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "usuario@example.com"
    assert response.json()["role"] == UserRole.USER.value


def test_me_rejects_invalid_token(api_client):
    response = api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401


# Alteracao de senha


def test_change_password_rejects_request_without_token(api_client):
    response = api_client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": VALID_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 401


def test_change_password_rejects_mismatched_confirmation(api_client):
    login = register_and_login(api_client)

    response = api_client.post(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {login['access_token']}",
        },
        json={
            "current_password": VALID_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": "OutraSenha789!",
        },
    )

    assert response.status_code == 400


def test_change_password_rejects_incorrect_current_password(api_client):
    login = register_and_login(api_client)

    response = api_client.post(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": f"Bearer {login['access_token']}",
        },
        json={
            "current_password": "SenhaErrada123!",
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 400


def test_change_password_returns_new_token_and_invalidates_old_token(
    api_client,
):
    login = register_and_login(api_client)
    old_token = login["access_token"]

    change_response = api_client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {old_token}"},
        json={
            "current_password": VALID_PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert change_response.status_code == 200

    body = change_response.json()
    assert body["access_token"]
    assert body["access_token"] != old_token

    old_token_response = api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert old_token_response.status_code == 401

    new_token_response = api_client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {body['access_token']}",
        },
    )
    assert new_token_response.status_code == 200


# Inicializacao administrativa


def test_admin_bootstrap_returns_service_unavailable_when_unconfigured(
    api_client,
    monkeypatch,
):
    monkeypatch.setenv("MATCHCV_ADMIN_BOOTSTRAP_TOKEN", "")

    response = api_client.post(
        "/api/v1/auth/admin/bootstrap",
        json={
            "name": "Administrador Inicial",
            "email": "admin@admin.com",
            "password": VALID_PASSWORD,
        },
        headers={"X-Admin-Bootstrap-Token": "token-de-teste"},
    )

    assert response.status_code == 503


def test_admin_bootstrap_rejects_invalid_bootstrap_token(
    api_client,
    monkeypatch,
):
    monkeypatch.setenv(
        "MATCHCV_ADMIN_BOOTSTRAP_TOKEN",
        "token-administrativo-seguro-com-mais-de-32-bytes",
    )

    response = api_client.post(
        "/api/v1/auth/admin/bootstrap",
        json={
            "name": "Administrador Inicial",
            "email": "admin@admin.com",
            "password": VALID_PASSWORD,
        },
        headers={"X-Admin-Bootstrap-Token": "token-incorreto"},
    )

    assert response.status_code == 403


def test_admin_bootstrap_rejects_wrong_email(
    api_client,
    monkeypatch,
):
    bootstrap_token = "token-administrativo-seguro-com-mais-de-32-bytes"
    monkeypatch.setenv("MATCHCV_ADMIN_BOOTSTRAP_TOKEN", bootstrap_token)

    response = api_client.post(
        "/api/v1/auth/admin/bootstrap",
        json={
            "name": "Administrador Inicial",
            "email": "outro@example.com",
            "password": VALID_PASSWORD,
        },
        headers={"X-Admin-Bootstrap-Token": bootstrap_token},
    )

    assert response.status_code == 400


def test_admin_bootstrap_creates_admin(
    api_client,
    monkeypatch,
):
    bootstrap_token = "token-administrativo-seguro-com-mais-de-32-bytes"
    monkeypatch.setenv("MATCHCV_ADMIN_BOOTSTRAP_TOKEN", bootstrap_token)

    response = api_client.post(
        "/api/v1/auth/admin/bootstrap",
        json={
            "name": "Administrador Inicial",
            "email": "admin@admin.com",
            "password": VALID_PASSWORD,
        },
        headers={"X-Admin-Bootstrap-Token": bootstrap_token},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "admin@admin.com"
    assert response.json()["role"] == UserRole.ADMIN.value


def test_admin_bootstrap_rejects_second_admin(
    api_client,
    monkeypatch,
):
    bootstrap_token = "token-administrativo-seguro-com-mais-de-32-bytes"
    monkeypatch.setenv("MATCHCV_ADMIN_BOOTSTRAP_TOKEN", bootstrap_token)

    payload = {
        "name": "Administrador Inicial",
        "email": "admin@admin.com",
        "password": VALID_PASSWORD,
    }
    headers = {"X-Admin-Bootstrap-Token": bootstrap_token}

    first_response = api_client.post(
        "/api/v1/auth/admin/bootstrap",
        json=payload,
        headers=headers,
    )
    second_response = api_client.post(
        "/api/v1/auth/admin/bootstrap",
        json=payload,
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
