from ..feeds import ashby_internships_us

COMPANY_NAME = "Confluent"
CAREERS_URL = "https://careers.confluent.io/"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("confluent")
