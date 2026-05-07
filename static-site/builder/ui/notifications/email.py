"""notifications/email.py — Email notification provider (SMTP)."""
from __future__ import annotations
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailProvider:
    """SMTP email provider. Configure via environment variables."""

    def __init__(self):
        self._host     = os.environ.get("SMTP_HOST", "")
        self._port     = int(os.environ.get("SMTP_PORT", "587"))
        self._user     = os.environ.get("SMTP_USER", "")
        self._password = os.environ.get("SMTP_PASSWORD", "")
        self._from     = os.environ.get("SMTP_FROM", self._user)

    def is_configured(self) -> bool:
        return bool(self._host and self._user)

    def send(self, user_id: str, notification_type: str, payload: dict) -> bool:
        if not self.is_configured():
            return False
        to_email = payload.get("email", "")
        if not to_email:
            return False
        from notifications.dispatcher import TEMPLATES
        tpl     = TEMPLATES.get(notification_type, {})
        subject = tpl.get("subject", notification_type)
        body    = tpl.get("body", "").format(**payload)
        return self._send_email(to_email, subject, body)

    def _send_email(self, to: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = self._from
            msg["To"]      = to
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(self._host, self._port, timeout=10) as s:
                s.starttls()
                s.login(self._user, self._password)
                s.sendmail(self._from, [to], msg.as_string())
            return True
        except Exception:
            return False
