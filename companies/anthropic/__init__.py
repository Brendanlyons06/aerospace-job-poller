from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Anthropic"
CAREERS_URL = "https://www.anthropic.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("anthropic")
