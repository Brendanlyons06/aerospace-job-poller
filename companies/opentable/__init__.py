from ..feeds import greenhouse_internships_us

COMPANY_NAME = "OpenTable"
CAREERS_URL = "https://job-boards.greenhouse.io/opentable"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("opentable")
