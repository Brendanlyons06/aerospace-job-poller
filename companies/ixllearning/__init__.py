from ..feeds import greenhouse_internships_us

COMPANY_NAME = "IXL Learning"
CAREERS_URL = "https://www.ixl.com/company/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("ixllearning")
