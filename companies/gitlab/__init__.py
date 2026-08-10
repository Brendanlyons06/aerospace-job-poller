from ..feeds import greenhouse_internships_us

COMPANY_NAME = "GitLab"
CAREERS_URL = "https://about.gitlab.com/company/culture/all-remote/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("gitlab")
