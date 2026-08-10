from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Klaviyo"
CAREERS_URL = "https://job-boards.greenhouse.io/klaviyo"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("klaviyo")
