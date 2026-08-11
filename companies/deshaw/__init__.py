"""The D. E. Shaw Group's internships from its own careers page."""

from ...filters import internships_in_us
from . import client

COMPANY_NAME = "D. E. Shaw"
CAREERS_URL = "https://www.deshaw.com/careers"


def fetch_jobs() -> list[dict]:
    # Office names are bare cities ("New York", "London"); the US predicate
    # recognizes the state-named ones, which is exactly the split wanted.
    return internships_in_us(client.internships())
