from MatchCV.Infrastructure.Services.PasswordResetEmailSender import (
    PasswordResetEmailSender,
)


class FakeSMTP:
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent_message = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def ehlo(self):
        return None

    def starttls(self):
        self.started_tls = True

    def login(self, username, password):
        self.logged_in = True

    def send_message(self, message):
        self.sent_message = message


def test_sender_sends_recovery_link_over_starttls(monkeypatch):
    import smtplib

    created = {}

    def smtp_factory(host, port, timeout):
        server = FakeSMTP(host, port, timeout)
        created["server"] = server
        return server

    monkeypatch.setattr(smtplib, "SMTP", smtp_factory)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "matchcv@example.test")
    monkeypatch.setenv("SMTP_PASSWORD", "not-a-real-password")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "no-reply@example.test")
    monkeypatch.setenv("SMTP_FROM_NAME", "MatchCV")

    PasswordResetEmailSender().send_recovery_instructions(
        "user@example.test",
        "https://matchcv.example/forgot-password#token=synthetic-token",
    )

    server = created["server"]
    assert server.started_tls
    assert server.logged_in
    assert server.sent_message["To"] == "user@example.test"
    assert "synthetic-token" in server.sent_message.get_content()
