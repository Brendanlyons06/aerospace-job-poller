from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Twitch"
CAREERS_URL = "https://job-boards.greenhouse.io/twitch"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("twitch")
