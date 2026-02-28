import logging
import smtplib
from email.message import EmailMessage

from ..config import settings

logger = logging.getLogger(__name__)


def notify_parent_student_created(
    *,
    parent_email: str,
    student_name: str,
    student_id: str,
    initial_pin: str,
) -> bool:
    if not settings.send_parent_email_on_student_create:
        return True

    max_attempts = max(1, int(settings.email_retry_attempts))
    for attempt in range(1, max_attempts + 1):
        try:
            _send_student_created_email(
                parent_email=parent_email,
                student_name=student_name,
                student_id=student_id,
                initial_pin=initial_pin,
            )
            return True
        except Exception as exc:
            logger.warning(
                "student_created_email_failed attempt=%s/%s parent=%s error=%s",
                attempt,
                max_attempts,
                parent_email,
                exc,
            )
    return False


def _send_student_created_email(
    *,
    parent_email: str,
    student_name: str,
    student_id: str,
    initial_pin: str,
) -> None:
    if not settings.smtp_host:
        raise RuntimeError("SMTP host is not configured")

    sender = settings.smtp_sender or settings.smtp_username or "no-reply@ajmathtutor.local"
    msg = EmailMessage()
    msg["Subject"] = "AJ Math Tutor: New student account created"
    msg["From"] = sender
    msg["To"] = parent_email
    msg.set_content(
        "\n".join(
            [
                "A new student account has been created.",
                f"Student name: {student_name}",
                f"Student ID: {student_id}",
                f"Initial PIN: {initial_pin}",
                "",
                "For security, please ask the student to update the PIN after first login.",
            ]
        )
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(msg)
