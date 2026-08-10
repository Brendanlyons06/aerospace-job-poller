from ..feeds import ashby_internships_us

COMPANY_NAME = "OpenRouter"
CAREERS_URL = "https://jobs.ashbyhq.com/openrouter"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("openrouter")
