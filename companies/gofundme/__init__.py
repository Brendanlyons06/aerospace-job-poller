from ..feeds import greenhouse_internships_us

COMPANY_NAME = "GoFundMe"
CAREERS_URL = "https://www.gofundme.com/c/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("gofundme")
