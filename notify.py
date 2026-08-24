"""Barebones text + email senders. Reads credentials from .env at project root.

SMS goes through Twilio's REST API directly (curl_cffi call, no Twilio
SDK dependency). Email goes through Gmail SMTP with an app password.
"""

import os
import smtplib
from email.utils import getaddresses
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

from . import http

load_dotenv(Path(__file__).resolve().parent / ".env")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")
TWILIO_TO_NUMBER = os.environ.get("TWILIO_TO_NUMBER", "")
SMS_ALERTS_ENABLED = os.environ.get("SMS_ALERTS_ENABLED", "").strip().lower() in ("1", "true", "yes")

OPT_IN_SENT_MARKER = Path(__file__).resolve().parent / ".sms_opt_in_sent"
OPT_IN_MESSAGE = (
    "Career Watch: You opted in to job alert texts by enabling SMS alerts "
    "in the app settings. Msg frequency varies. Msg & data rates may apply. "
    "Reply STOP to unsubscribe, HELP for help."
)

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")
EMAIL_ALERTS_ENABLED = os.environ.get("EMAIL_ALERTS_ENABLED", "").strip().lower() in (
    "1",
    "true",
    "yes",
)


def _email_recipients() -> list[str]:
    """Parse and normalize the configured comma-separated recipients."""
    return [
        address.strip()
        for _, address in getaddresses([EMAIL_TO])
        if address and address.strip()
    ]


def validate_configuration() -> tuple[str, ...]:
    """Validate enabled alert channels before a poll can mark jobs as seen."""
    enabled = []
    errors = []

    if EMAIL_ALERTS_ENABLED:
        enabled.append("email")
        if not SMTP_USER:
            errors.append("SMTP_USER is required when email alerts are enabled")
        if not SMTP_PASSWORD:
            errors.append("SMTP_PASSWORD is required when email alerts are enabled")
        if not _email_recipients():
            errors.append("EMAIL_TO must contain at least one recipient")

    if SMS_ALERTS_ENABLED:
        enabled.append("sms")
        missing = [
            name
            for name, value in (
                ("TWILIO_ACCOUNT_SID", TWILIO_ACCOUNT_SID),
                ("TWILIO_AUTH_TOKEN", TWILIO_AUTH_TOKEN),
                ("TWILIO_FROM_NUMBER", TWILIO_FROM_NUMBER),
                ("TWILIO_TO_NUMBER", TWILIO_TO_NUMBER),
            )
            if not value
        ]
        if missing:
            errors.append(
                "Twilio settings missing: " + ", ".join(missing)
            )

    if not enabled:
        errors.append(
            "No alert channel is enabled; set EMAIL_ALERTS_ENABLED=true "
            "or SMS_ALERTS_ENABLED=true"
        )
    if errors:
        raise RuntimeError("Invalid notification configuration: " + "; ".join(errors))
    return tuple(enabled)


def send_text(body: str) -> None:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER and TWILIO_TO_NUMBER):
        raise RuntimeError("Twilio env vars not set (see .env.example)")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    # Twilio POSTs create messages, so retrying after an ambiguous failure
    # could deliver a duplicate alert.
    with http.session(retries=0) as session:
        resp = session.post(
            url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            data={"From": TWILIO_FROM_NUMBER, "To": TWILIO_TO_NUMBER, "Body": body},
        )
        resp.raise_for_status()


def send_email(subject: str, body: str) -> None:
    recipients = _email_recipients()
    if not (SMTP_USER and SMTP_PASSWORD and recipients):
        raise RuntimeError("SMTP env vars not set (see .env.example)")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg, to_addrs=recipients)


def ensure_opted_in() -> None:
    """Send the one-time SMS opt-in confirmation the first time alerts are enabled."""
    if not SMS_ALERTS_ENABLED or OPT_IN_SENT_MARKER.exists():
        return
    send_text(OPT_IN_MESSAGE)
    OPT_IN_SENT_MARKER.write_text("sent\n")


def _deliver(subject: str, body: str, *, sms_body: str | None = None) -> tuple[str, ...]:
    """Send a message through enabled channels, isolating channel failures."""
    channels = validate_configuration()
    delivered = []
    failures = []

    if "sms" in channels:
        try:
            send_text(sms_body or f"{subject}\n{body}")
            delivered.append("sms")
        except Exception as exc:
            failures.append(f"sms: {type(exc).__name__}: {exc}")

    if "email" in channels:
        try:
            send_email(subject, body)
            delivered.append("email")
        except Exception as exc:
            failures.append(f"email: {type(exc).__name__}: {exc}")

    if failures and not delivered:
        raise RuntimeError("All notification deliveries failed: " + "; ".join(failures))
    if failures:
        print("NOTIFICATION WARNING: " + "; ".join(failures))
    return tuple(delivered)


def notify_new_job(company: str, job: dict) -> tuple[str, ...]:
    """Send a job through every enabled channel, isolating channel failures."""
    subject = f"New {company} posting: {job['title']}"
    body = f"{job['title']}\n{', '.join(job['locations'])}\n{job.get('url', '')}"
    return _deliver(
        subject,
        body,
        sms_body=f"{subject}\n{', '.join(job['locations'])}\n{job.get('url', '')}",
    )


def notify_system_message(subject: str, body: str) -> tuple[str, ...]:
    """Send a poller health or recovery message through enabled channels."""
    return _deliver(subject, body)
