from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Qualtrics"
CAREERS_URL = "https://job-boards.greenhouse.io/qualtrics"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("qualtrics")
