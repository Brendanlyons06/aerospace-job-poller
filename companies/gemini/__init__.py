from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Gemini"
CAREERS_URL = "https://job-boards.greenhouse.io/gemini"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("gemini")
