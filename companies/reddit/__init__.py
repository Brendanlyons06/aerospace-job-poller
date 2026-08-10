from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Reddit"
CAREERS_URL = "https://www.redditinc.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("reddit")
