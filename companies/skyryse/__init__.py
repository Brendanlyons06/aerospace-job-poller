from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Skyryse"
CAREERS_URL = "https://skyryse.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("skyryse")
