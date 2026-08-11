from ..feeds import ashby_internships_us

COMPANY_NAME = "Talos"
CAREERS_URL = "https://talos.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("Talos-Trading")
