from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Astranis"
CAREERS_URL = "https://job-boards.greenhouse.io/astranis"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("astranis")
