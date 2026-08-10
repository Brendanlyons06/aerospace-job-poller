from ..feeds import ashby_internships_us

COMPANY_NAME = "LlamaIndex"
CAREERS_URL = "https://jobs.ashbyhq.com/llamaindex"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("llamaindex")
