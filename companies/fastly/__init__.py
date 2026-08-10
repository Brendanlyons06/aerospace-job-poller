from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Fastly"
CAREERS_URL = "https://job-boards.greenhouse.io/fastly"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("fastly")
