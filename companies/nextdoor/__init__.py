from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Nextdoor"
CAREERS_URL = "https://job-boards.greenhouse.io/nextdoor"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("nextdoor")
