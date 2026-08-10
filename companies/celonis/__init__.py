from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Celonis"
CAREERS_URL = "https://job-boards.greenhouse.io/celonis"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("celonis")
