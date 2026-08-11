from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Moloco"
CAREERS_URL = "https://www.moloco.com/careers"


def fetch_jobs() -> list[dict]:
    # Moloco also posts Seoul-based internships; the US office filter in
    # greenhouse_internships_us keeps only the US ones.
    return greenhouse_internships_us("moloco")
