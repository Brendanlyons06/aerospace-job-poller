from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Tripadvisor"
CAREERS_URL = "https://job-boards.greenhouse.io/tripadvisor"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("tripadvisor")
