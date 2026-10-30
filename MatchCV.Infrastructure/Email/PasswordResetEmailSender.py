import os
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode


class PasswordResetEmailSender:
    """Envia instruções de recuperação por SMTP configurado no ambiente."""

    def __init__(self) -> None:
        self._host = os.getenv("SMTP_HOST", "").strip()
        self._port = int(os.getenv("SMTP_PORT", "587"))
        self._username = os.getenv("SMTP_USERNAME", "").strip()
        self._password = os.getenv("SMTP_PASSWORD", "")
        self._sender = os.getenv("SMTP_FROM_EMAIL", "").strip()
        self._frontend_url = os.getenv("PASSWORD_RESET_FRONTEND_URL", "").strip()
        self._use_ssl = os.getenv("SMTP_USE_SSL", "false").strip().lower() in {"1", "true", "yes"}
        self._starttls = os.getenv("SMTP_STARTTLS", "true").strip().lower() in {"1", "true", "yes"}

    @property
    def is_configured(self) -> bool:
        return bool(self._host and self._sender and self._frontend_url)

    def send(self, email: str, token: str) -> bool:
        if not self.is_configured:
            return False

        query = urlencode({"token": token})
        reset_url = f"{self._frontend_url.rstrip('/')}?{query}"
        message = EmailMessage()
        message["Subject"] = "Recuperação de senha do MatchCV"
        message["From"] = self._sender
        message["To"] = email
        message.set_content(
            "Recebemos uma solicitação para redefinir a senha da sua conta MatchCV.\n\n"
            f"Use o link abaixo em até 15 minutos. Ele só pode ser utilizado uma vez:\n{reset_url}\n\n"
            "Se você não solicitou a recuperação, ignore esta mensagem."
        )

        if self._use_ssl:
            with smtplib.SMTP_SSL(self._host, self._port, timeout=15) as smtp:
                if self._username:
                    smtp.login(self._username, self._password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(self._host, self._port, timeout=15) as smtp:
                smtp.ehlo()
                if self._starttls:
                    smtp.starttls()
                    smtp.ehlo()
                if self._username:
                    smtp.login(self._username, self._password)
                smtp.send_message(message)
        return True
