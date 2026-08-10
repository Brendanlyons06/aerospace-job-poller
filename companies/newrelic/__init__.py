from ..feeds import greenhouse_internships_us

COMPANY_NAME = "New Relic"
CAREERS_URL = "https://job-boards.greenhouse.io/newrelic"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("newrelic")
