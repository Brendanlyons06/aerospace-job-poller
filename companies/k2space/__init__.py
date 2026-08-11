from ..feeds import greenhouse_internships_us

COMPANY_NAME = "K2 Space"
CAREERS_URL = "https://job-boards.greenhouse.io/k2spacecorporation"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("k2spacecorporation")
