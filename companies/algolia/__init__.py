from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Algolia"
CAREERS_URL = "https://job-boards.greenhouse.io/algolia"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("algolia")
