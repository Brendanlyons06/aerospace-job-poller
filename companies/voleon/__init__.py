from ..feeds import lever_internships_us

COMPANY_NAME = "The Voleon Group"
CAREERS_URL = "https://voleon.com/careers/"


def fetch_jobs() -> list[dict]:
    # Voleon's Lever board currently exposes 0 public postings; they list
    # seasonally, so keep polling the confirmed-valid endpoint.
    return lever_internships_us("voleon")
