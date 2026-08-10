from ..feeds import greenhouse_internships_us

COMPANY_NAME = "PagerDuty"
CAREERS_URL = "https://job-boards.greenhouse.io/pagerduty"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("pagerduty")
