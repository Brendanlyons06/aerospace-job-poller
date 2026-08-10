from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Squarespace"
CAREERS_URL = "https://job-boards.greenhouse.io/squarespace"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("squarespace")
