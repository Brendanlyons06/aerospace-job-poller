from ..feeds import greenhouse_internships_us

COMPANY_NAME = "StarTree"
CAREERS_URL = "https://startree.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("startree")
