"""Citadel internships from its own open-opportunities listing."""

from ...filters import internships_in_us
from . import client

COMPANY_NAME = "Citadel"
CAREERS_URL = "https://www.citadel.com/careers/open-opportunities/"


def fetch_jobs() -> list[dict]:
    return internships_in_us(client.open_positions())
