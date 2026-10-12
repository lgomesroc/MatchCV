import base64
import hashlib
import hmac
import secrets


class PasswordHasher:
    """Gera e verifica hashes de senha com PBKDF2-HMAC-SHA256."""

    ITERATIONS = 600_000

    @classmethod
    def hash_password(cls, password: str) -> str:
        if not password:
            raise ValueError("A senha é obrigatória.")

        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls.ITERATIONS,
        )

        salt_encoded = base64.urlsafe_b64encode(salt).decode("ascii")
        digest_encoded = base64.urlsafe_b64encode(digest).decode("ascii")

        return (
            f"pbkdf2_sha256${cls.ITERATIONS}"
            f"${salt_encoded}${digest_encoded}"
        )

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations_text, salt_text, digest_text = (
                password_hash.split("$")
            )

            if algorithm != "pbkdf2_sha256":
                return False

            iterations = int(iterations_text)
            salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
            expected_digest = base64.urlsafe_b64decode(
                digest_text.encode("ascii")
            )

            actual_digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
            )

            return hmac.compare_digest(actual_digest, expected_digest)
        except (ValueError, TypeError, UnicodeError):
            return False
