from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Krea"
CAREERS_URL = "https://jobs.ashbyhq.com/krea"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("krea")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
