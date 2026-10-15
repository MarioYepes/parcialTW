"""Envio de correos transaccionales mediante SMTP."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import settings


def send_otp_email(recipient: str, code: str) -> None:
    """Envia un codigo OTP al correo indicado.

    En desarrollo (sin SMTP real configurado) imprime el codigo en consola.
    """
    if not settings.smtp_host or settings.smtp_host == "smtp.example.com":
        print(f"[DEV] OTP para {recipient}: {code}", flush=True)
        return

    message = EmailMessage()
    message["Subject"] = "Tu codigo de verificacion"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(
        f"Tu codigo de verificacion es {code}. "
        f"Expira en {settings.otp_expire_minutes} minutos."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
