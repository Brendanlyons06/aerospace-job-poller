"""Barebones text + email senders. Reads credentials from .env at project root.

SMS goes through Twilio's REST API directly (plain requests call, no twilio
SDK dependency). Email goes through Gmail SMTP with an app password.
"""

import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

import requests
from dotenv import load_dotenv

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


def send_text(body: str) -> None:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER and TWILIO_TO_NUMBER):
        raise RuntimeError("Twilio env vars not set (see .env.example)")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    resp = requests.post(
        url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        data={"From": TWILIO_FROM_NUMBER, "To": TWILIO_TO_NUMBER, "Body": body},
    )
    resp.raise_for_status()


def send_email(subject: str, body: str) -> None:
    if not (SMTP_USER and SMTP_PASSWORD and EMAIL_TO):
        raise RuntimeError("SMTP env vars not set (see .env.example)")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def ensure_opted_in() -> None:
    """Send the one-time SMS opt-in confirmation the first time alerts are enabled."""
    if not SMS_ALERTS_ENABLED or OPT_IN_SENT_MARKER.exists():
        return
    send_text(OPT_IN_MESSAGE)
    OPT_IN_SENT_MARKER.write_text("sent\n")


def notify_new_job(company: str, job: dict) -> None:
    subject = f"New {company} posting: {job['title']}"
    body = f"{job['title']}\n{', '.join(job['locations'])}\n{job.get('url', '')}"
    send_text(f"{subject}\n{', '.join(job['locations'])}")
    send_email(subject, body)
