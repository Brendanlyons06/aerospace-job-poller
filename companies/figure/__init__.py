from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Figure"
CAREERS_URL = "https://www.figure.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("figureai")
