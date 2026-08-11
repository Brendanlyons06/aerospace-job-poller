from ..feeds import greenhouse_internships_us

COMPANY_NAME = "CoreWeave"
CAREERS_URL = "https://www.coreweave.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("coreweave")
