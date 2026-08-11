from ..feeds import ashby_internships_us

COMPANY_NAME = "Lambda"
CAREERS_URL = "https://lambda.ai/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("lambda")
