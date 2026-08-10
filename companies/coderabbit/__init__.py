from ..feeds import ashby_internships_us

COMPANY_NAME = "CodeRabbit"
CAREERS_URL = "https://jobs.ashbyhq.com/coderabbit"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("coderabbit")
