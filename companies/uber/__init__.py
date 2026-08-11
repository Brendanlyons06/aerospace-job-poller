"""Uber US SWE/ML internships from its Oracle Recruiting Cloud API."""

from ...filters import internships_in_us
from . import client

COMPANY_NAME = "Uber"
CAREERS_URL = "https://jobs.uber.com/en/jobs/"


def fetch_jobs() -> list[dict]:
    # Oracle's keyword search is fuzzy (matches "international" etc.), so
    # validate internship, role, and country strictly from title + location.
    return internships_in_us(client.search_requisitions("intern"))
