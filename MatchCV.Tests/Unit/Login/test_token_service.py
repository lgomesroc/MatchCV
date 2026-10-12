import os
import time

import pytest

from MatchCV.Login.Tokens.TokenService import TokenService


@pytest.fixture
def token_service(monkeypatch):
    monkeypatch.setenv("MATCHCV_JWT_SECRET", "chave-de-teste-com-mais-de-32-bytes")
    monkeypatch.setenv("MATCHCV_ACCESS_TOKEN_MINUTES", "30")
    return TokenService()


def test_creates_and_decodes_access_token(token_service):
    token = token_service.create_access_token("12345678-1234-5678-1234-567812345678")

    payload = token_service.decode_access_token(token)

    assert payload["sub"] == "12345678-1234-5678-1234-567812345678"
    assert payload["exp"] > payload["iat"]


def test_rejects_token_with_tampered_signature(token_service):
    token = token_service.create_access_token("user-123")
    header, payload, signature = token.split(".")
    replacement = "A" if signature[0] != "A" else "B"
    tampered_token = f"{header}.{payload}.{replacement}{signature[1:]}"

    with pytest.raises(ValueError, match="inválido ou expirado"):
        token_service.decode_access_token(tampered_token)


@pytest.mark.parametrize("token", ["", "abc", "a.b.c.d", "not-a-token"])
def test_rejects_malformed_token(token_service, token):
    with pytest.raises(ValueError, match="inválido ou expirado"):
        token_service.decode_access_token(token)


def test_rejects_expired_token(token_service, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 2_000_000_000)
    token = token_service.create_access_token("user-123")

    monkeypatch.setattr(time, "time", lambda: 2_000_000_000 + 31 * 60)

    with pytest.raises(ValueError, match="inválido ou expirado"):
        token_service.decode_access_token(token)


def test_requires_secret_with_at_least_32_bytes(monkeypatch):
    monkeypatch.setenv("MATCHCV_JWT_SECRET", "curta")

    with pytest.raises(RuntimeError, match="32 bytes"):
        TokenService()
