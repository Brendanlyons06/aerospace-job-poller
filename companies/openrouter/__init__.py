from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "OpenRouter"
CAREERS_URL = "https://jobs.ashbyhq.com/openrouter"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("openrouter")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
