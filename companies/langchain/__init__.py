from ..feeds import ashby_internships_us

COMPANY_NAME = "LangChain"
CAREERS_URL = "https://jobs.ashbyhq.com/langchain"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("langchain")
