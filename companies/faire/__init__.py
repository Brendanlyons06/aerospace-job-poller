from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Faire"
CAREERS_URL = "https://job-boards.greenhouse.io/faire"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("faire")
