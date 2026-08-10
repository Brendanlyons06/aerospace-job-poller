from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Vapi"
CAREERS_URL = "https://jobs.ashbyhq.com/vapi"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("vapi")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
