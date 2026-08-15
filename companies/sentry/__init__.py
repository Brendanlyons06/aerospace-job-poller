from ..feeds import ashby_internships_us

COMPANY_NAME = "Sentry"
CAREERS_URL = "https://sentry.io/careers/"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("sentry")
