from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Coursera"
CAREERS_URL = "https://job-boards.greenhouse.io/coursera"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("coursera")
