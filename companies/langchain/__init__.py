from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "LangChain"
CAREERS_URL = "https://jobs.ashbyhq.com/langchain"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("langchain")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
