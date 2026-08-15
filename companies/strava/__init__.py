from ..feeds import ashby_internships_us

COMPANY_NAME = "Strava"
CAREERS_URL = "https://www.strava.com/careers"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("strava")
