from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Together AI"
CAREERS_URL = "https://www.together.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("togetherai")
