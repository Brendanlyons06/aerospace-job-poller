from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Deepgram"
CAREERS_URL = "https://jobs.ashbyhq.com/deepgram"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("deepgram")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
