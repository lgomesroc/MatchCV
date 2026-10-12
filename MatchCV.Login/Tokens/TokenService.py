import base64
import hashlib
import hmac
import json
import os
import time

from dotenv import load_dotenv

load_dotenv()


class TokenService:
    """Emite e valida tokens assinados com HMAC-SHA256."""

    def __init__(self) -> None:
        secret = os.getenv("MATCHCV_JWT_SECRET", "")
        if len(secret.encode("utf-8")) < 32:
            raise RuntimeError(
                "MATCHCV_JWT_SECRET precisa ter pelo menos 32 bytes. "
                "Configure essa variável no arquivo .env."
            )
        self._secret = secret.encode("utf-8")
        self._lifetime_seconds = int(
            os.getenv("MATCHCV_ACCESS_TOKEN_MINUTES", "30")
        ) * 60

    @staticmethod
    def _encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _decode(value: str) -> bytes:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

    @staticmethod
    def password_version(password_hash: str) -> str:
        return hashlib.sha256(password_hash.encode("utf-8")).hexdigest()

    def create_access_token(
        self, subject: str, password_hash: str | None = None
    ) -> str:
        now = int(time.time())
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + self._lifetime_seconds,
        }
        if password_hash is not None:
            payload["pwdv"] = self.password_version(password_hash)

        header = {"alg": "HS256", "typ": "JWT"}
        encoded_header = self._encode(
            json.dumps(header, separators=(",", ":")).encode("utf-8")
        )
        encoded_payload = self._encode(
            json.dumps(payload, separators=(",", ":")).encode("utf-8")
        )
        unsigned_token = f"{encoded_header}.{encoded_payload}"
        signature = hmac.new(
            self._secret, unsigned_token.encode("ascii"), hashlib.sha256
        ).digest()
        return f"{unsigned_token}.{self._encode(signature)}"

    def decode_access_token(self, token: str) -> dict:
        try:
            encoded_header, encoded_payload, encoded_signature = token.split(".")
            header = json.loads(self._decode(encoded_header))
            payload = json.loads(self._decode(encoded_payload))

            if header.get("alg") != "HS256":
                raise ValueError("Algoritmo de token inválido.")

            unsigned_token = f"{encoded_header}.{encoded_payload}"
            expected_signature = hmac.new(
                self._secret, unsigned_token.encode("ascii"), hashlib.sha256
            ).digest()
            received_signature = self._decode(encoded_signature)

            if not hmac.compare_digest(expected_signature, received_signature):
                raise ValueError("Assinatura inválida.")
            if int(payload.get("exp", 0)) <= int(time.time()):
                raise ValueError("Token expirado.")
            if not payload.get("sub"):
                raise ValueError("Token sem identificador de usuário.")

            return payload
        except (
            ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError
        ) as exception:
            raise ValueError("Token de acesso inválido ou expirado.") from exception
