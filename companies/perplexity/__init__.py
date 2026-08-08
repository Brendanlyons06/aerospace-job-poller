from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Perplexity"
CAREERS_URL = "https://www.perplexity.ai/hub/careers"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("perplexity")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
