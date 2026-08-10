from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Okta"
CAREERS_URL = "https://www.okta.com/company/careers/job-listing/"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("okta")
