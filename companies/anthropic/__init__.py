from ..feeds import anthropic_jobs, technical_internships

COMPANY_NAME = "Anthropic"
CAREERS_URL = "https://www.anthropic.com/careers"

def fetch_jobs() -> list[dict]:
    return anthropic_jobs()

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
