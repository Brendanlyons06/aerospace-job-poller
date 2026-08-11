"""Microsoft US SWE/ML internships from its Eightfold pcsx search API."""

from ...filters import internships_in_us
from . import client

COMPANY_NAME = "Microsoft"
CAREERS_URL = "https://careers.microsoft.com/"


def fetch_jobs() -> list[dict]:
    # The API enforces the country filter itself, but its keyword search is
    # fuzzy ("intern" also hits "internal"), so validate internship, role,
    # and country strictly from title + location.
    return internships_in_us(client.search_positions("intern", "United States"))
