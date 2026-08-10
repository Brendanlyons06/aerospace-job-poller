from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Dropbox"
CAREERS_URL = "https://jobs.dropbox.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("dropbox")
