from ..feeds import greenhouse_internships_us

COMPANY_NAME = "ZipRecruiter"
CAREERS_URL = "https://www.ziprecruiter.com/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("ziprecruiter")
