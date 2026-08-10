from ..feeds import greenhouse_internships_us

COMPANY_NAME = "commercetools"
CAREERS_URL = "https://job-boards.greenhouse.io/commercetools"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("commercetools")
