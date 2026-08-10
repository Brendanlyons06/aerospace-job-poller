from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Marqeta"
CAREERS_URL = "https://job-boards.greenhouse.io/marqeta"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("marqeta")
