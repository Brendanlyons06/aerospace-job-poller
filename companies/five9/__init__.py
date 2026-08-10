from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Five9"
CAREERS_URL = "https://job-boards.greenhouse.io/five9"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("five9")
