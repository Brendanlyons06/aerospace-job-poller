from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "OpenAI"
CAREERS_URL = "https://openai.com/careers/"

def fetch_jobs() -> list[dict]:
    return ashby_jobs("openai")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
