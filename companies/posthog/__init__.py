from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "PostHog"
CAREERS_URL = "https://jobs.ashbyhq.com/posthog"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("posthog")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
