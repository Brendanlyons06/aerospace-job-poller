from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Flexport"
CAREERS_URL = "https://job-boards.greenhouse.io/flexport"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("flexport")
