from ..feeds import greenhouse_internships_us

COMPANY_NAME = "xAI"
CAREERS_URL = "https://x.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("xai")
