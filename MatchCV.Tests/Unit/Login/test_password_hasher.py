from MatchCV.Login.Authentication.PasswordHasher import PasswordHasher


def test_hashes_and_verifies_correct_password():
    password = "MatchCV123!"
    password_hash = PasswordHasher.hash_password(password)

    assert password_hash.startswith("pbkdf2_sha256$600000$")
    assert password_hash != password
    assert PasswordHasher.verify_password(password, password_hash)


def test_different_hashes_are_generated_for_same_password():
    first_hash = PasswordHasher.hash_password("MatchCV123!")
    second_hash = PasswordHasher.hash_password("MatchCV123!")

    assert first_hash != second_hash
    assert PasswordHasher.verify_password("MatchCV123!", first_hash)
    assert PasswordHasher.verify_password("MatchCV123!", second_hash)


def test_rejects_incorrect_password():
    password_hash = PasswordHasher.hash_password("MatchCV123!")

    assert not PasswordHasher.verify_password("OutraSenha123!", password_hash)


def test_rejects_malformed_hash():
    assert not PasswordHasher.verify_password("MatchCV123!", "hash-invalido")


def test_rejects_empty_password_when_hashing():
    import pytest

    with pytest.raises(ValueError, match="obrigatória"):
        PasswordHasher.hash_password("")
