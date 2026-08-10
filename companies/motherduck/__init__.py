from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "MotherDuck"
CAREERS_URL = "https://jobs.ashbyhq.com/motherduck"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("motherduck")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
