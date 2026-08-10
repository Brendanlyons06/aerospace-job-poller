from ..feeds import ashby_internships_us

COMPANY_NAME = "Semgrep"
CAREERS_URL = "https://jobs.ashbyhq.com/semgrep"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("semgrep")
