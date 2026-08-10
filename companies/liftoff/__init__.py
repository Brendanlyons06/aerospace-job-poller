from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Liftoff"
CAREERS_URL = "https://job-boards.greenhouse.io/liftoff"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("liftoff")
