from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Relativity"
CAREERS_URL = "https://job-boards.greenhouse.io/relativity"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("relativity")
