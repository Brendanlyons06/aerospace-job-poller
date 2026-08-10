from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Hedra"
CAREERS_URL = "https://jobs.ashbyhq.com/hedra"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("hedra")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
