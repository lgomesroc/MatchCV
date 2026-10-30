import os
import smtplib
from email.message import EmailMessage


class PasswordResetEmailSender:
    """Envia instruções de recuperação por SMTP autenticado e TLS."""

    def __init__(self) -> None:
        self._host = os.getenv("SMTP_HOST", "").strip()
        self._port = int(os.getenv("SMTP_PORT", "587"))
        self._username = os.getenv("SMTP_USERNAME", "").strip()
        self._password = os.getenv("SMTP_PASSWORD", "")
        self._from_email = os.getenv("SMTP_FROM_EMAIL", "").strip()
        self._from_name = os.getenv("SMTP_FROM_NAME", "MatchCV").strip()
        self._timeout = int(os.getenv("SMTP_TIMEOUT_SECONDS", "10"))

    def send_recovery_instructions(self, recipient: str, reset_url: str) -> None:
        missing = [
            name
            for name, value in (
                ("SMTP_HOST", self._host),
                ("SMTP_USERNAME", self._username),
                ("SMTP_PASSWORD", self._password),
                ("SMTP_FROM_EMAIL", self._from_email),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Configuração SMTP incompleta: " + ", ".join(missing)
            )

        message = EmailMessage()
        message["Subject"] = "Instruções para recuperar sua senha do MatchCV"
        message["From"] = f"{self._from_name} <{self._from_email}>"
        message["To"] = recipient
        message.set_content(
            "Recebemos uma solicitação para redefinir a senha da sua conta MatchCV.\n\n"
            "Para escolher uma nova senha, abra o link abaixo. Ele expira em 15 minutos "
            "e só pode ser usado uma vez:\n\n"
            f"{reset_url}\n\n"
            "Se você não solicitou a recuperação, ignore esta mensagem. "
            "Sua senha não será alterada."
        )

        with smtplib.SMTP(self._host, self._port, timeout=self._timeout) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self._username, self._password)
            server.send_message(message)
