from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Komodo Health"
CAREERS_URL = "https://job-boards.greenhouse.io/komodohealth"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("komodohealth")
