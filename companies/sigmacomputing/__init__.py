from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Sigma Computing"
CAREERS_URL = "https://sigmacomputing.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("sigmacomputing")
