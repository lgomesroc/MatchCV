import re


class PasswordPolicy:
    """Política de senha usada em todas as operações de criação de conta."""

    @staticmethod
    def validate(password: str) -> None:
        if len(password) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r"[a-z]", password):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r"[0-9]", password):
            raise ValueError("A senha deve conter pelo menos um número.")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("A senha deve conter pelo menos um caractere especial.")
