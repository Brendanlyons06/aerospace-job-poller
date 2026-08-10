from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Browserbase"
CAREERS_URL = "https://jobs.ashbyhq.com/browserbase"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("browserbase")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
