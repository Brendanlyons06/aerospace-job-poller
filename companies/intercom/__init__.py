from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Intercom"
CAREERS_URL = "https://job-boards.greenhouse.io/intercom"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("intercom")
