from ..feeds import amazon_jobs

COMPANY_NAME = "Amazon"
CAREERS_URL = "https://www.amazon.jobs/en/search?base_query=intern"


def fetch_jobs() -> list[dict]:
    return amazon_jobs()
