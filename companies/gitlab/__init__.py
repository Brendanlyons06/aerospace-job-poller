from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "GitLab"
CAREERS_URL = "https://about.gitlab.com/company/culture/all-remote/"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("gitlab")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
