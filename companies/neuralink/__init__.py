from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Neuralink"
CAREERS_URL = "https://neuralink.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("neuralink")
