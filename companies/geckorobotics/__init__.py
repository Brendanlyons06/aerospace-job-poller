from ..feeds import ashby_internships_us

COMPANY_NAME = "Gecko Robotics"
CAREERS_URL = "https://jobs.ashbyhq.com/gecko-robotics"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("gecko-robotics")
