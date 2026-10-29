from urllib.parse import urlparse, parse_qs

import pytest
from fastapi.testclient import TestClient

from MatchCV.Api.main import app
from MatchCV.Api.Routers.PasswordResetRouter import (
    get_password_reset_email_sender,
    get_password_reset_repository,
)

class FakeResetRepository:
    def __init__(self):
        self.accounts = {"user@example.com"}
        self.tokens = {}
        self.password_hashes = {}

    def create_token(self, email: str, token_hash: str) -> bool:
        if email not in self.accounts:
            return False
        self.tokens[token_hash] = {"email": email, "used": False}
        return True

    def revoke_token(self, token_hash: str) -> None:
        if token_hash in self.tokens:
            self.tokens[token_hash]["used"] = True

    def consume_token(self, token_hash: str, password_hash: str) -> bool:
        token = self.tokens.get(token_hash)
        if not token or token["used"]:
            return False
        token["used"] = True
        self.password_hashes[token["email"]] = password_hash
        return True


class FakeEmailSender:
    def __init__(self):
        self.sent = []

    def send_recovery_instructions(self, recipient: str, reset_url: str) -> None:
        self.sent.append((recipient, reset_url))


@pytest.fixture
def recovery_client(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    monkeypatch.setenv("PASSWORD_RESET_FRONTEND_URL", "https://matchcv.example")
    repository = FakeResetRepository()
    sender = FakeEmailSender()
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_password_reset_repository] = lambda: repository
    app.dependency_overrides[get_password_reset_email_sender] = lambda: sender
    with TestClient(app) as client:
        yield client, repository, sender
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def test_recovery_response_does_not_reveal_whether_email_exists(recovery_client):
    client, repository, sender = recovery_client
    existing = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "user@example.com"},
    )
    missing = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "missing@example.com"},
    )

    assert existing.status_code == missing.status_code == 200
    assert existing.json() == missing.json()
    assert "reset_token" not in existing.json()
    assert len(sender.sent) == 1
    assert sender.sent[0][0] == "user@example.com"
    assert "#token=" in sender.sent[0][1]


def test_production_never_returns_reset_token_even_if_legacy_flag_is_set(
    recovery_client, monkeypatch
):
    client, _, _ = recovery_client
    monkeypatch.setenv("MATCHCV_PASSWORD_RESET_EXPOSE_TOKEN", "true")

    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "user@example.com"},
    )

    assert response.status_code == 200
    assert "reset_token" not in response.json()


def test_token_is_single_use(recovery_client):
    client, repository, sender = recovery_client
    request_response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "user@example.com"},
    )
    assert request_response.status_code == 200
    token = parse_qs(urlparse(sender.sent[0][1]).fragment)["token"][0]

    payload = {
        "token": token,
        "new_password": "NovaSenha456@",
        "confirm_password": "NovaSenha456@",
    }
    first = client.post("/api/v1/auth/password-reset/confirm", json=payload)
    second = client.post("/api/v1/auth/password-reset/confirm", json=payload)

    assert first.status_code == 204
    assert second.status_code == 400
    assert "user@example.com" in repository.password_hashes



def test_failed_email_delivery_revokes_new_token(recovery_client):
    client, repository, sender = recovery_client

    def fail_send(recipient: str, reset_url: str) -> None:
        raise RuntimeError("SMTP unavailable")

    sender.send_recovery_instructions = fail_send
    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "user@example.com"},
    )

    assert response.status_code == 200
    assert response.json().get("reset_token") is None
    assert repository.tokens
    assert all(token["used"] for token in repository.tokens.values())
