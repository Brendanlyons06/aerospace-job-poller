from ..feeds import workday_internships_us

COMPANY_NAME = "CrowdStrike"
CAREERS_URL = "https://www.crowdstrike.com/careers/"


def fetch_jobs() -> list[dict]:
    return workday_internships_us("crowdstrike", "crowdstrikecareers")
