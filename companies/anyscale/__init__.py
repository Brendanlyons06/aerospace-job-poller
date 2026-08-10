from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Anyscale"
CAREERS_URL = "https://jobs.ashbyhq.com/anyscale"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("anyscale")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
