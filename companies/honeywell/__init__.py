"""Honeywell Aerospace-relevant U.S. engineering internships."""

from ...filters import aerospace_mechanical_internships_us
from . import client

COMPANY_NAME = "Honeywell Aerospace"
CAREERS_URL = "https://careers.honeywell.com/en/sites/Honeywell/jobs"


def fetch_jobs() -> list[dict]:
    return aerospace_mechanical_internships_us(client.search_requisitions())
