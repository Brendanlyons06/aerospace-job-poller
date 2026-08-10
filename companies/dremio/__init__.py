from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Dremio"
CAREERS_URL = "https://job-boards.greenhouse.io/dremio"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("dremio")
