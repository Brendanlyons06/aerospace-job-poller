from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Braze"
CAREERS_URL = "https://job-boards.greenhouse.io/braze"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("braze")
