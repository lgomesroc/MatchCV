import pytest

from MatchCV.Login.Authentication.PasswordPolicy import PasswordPolicy


@pytest.mark.parametrize(
    "password",
    [
        "MatchCV1!",
        "SenhaForte9@",
        "Abcdef12#",
    ],
)
def test_accepts_password_meeting_all_requirements(password):
    PasswordPolicy.validate(password)


@pytest.mark.parametrize(
    ("password", "message"),
    [
        ("Ab1!", "pelo menos 8 caracteres"),
        ("senhaforte1!", "letra maiúscula"),
        ("SENHAFORTE1!", "letra minúscula"),
        ("SenhaForte!", "número"),
        ("SenhaForte1", "caractere especial"),
    ],
)
def test_rejects_password_that_breaks_a_requirement(password, message):
    with pytest.raises(ValueError, match=message):
        PasswordPolicy.validate(password)
