from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "LlamaIndex"
CAREERS_URL = "https://jobs.ashbyhq.com/llamaindex"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("llamaindex")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
