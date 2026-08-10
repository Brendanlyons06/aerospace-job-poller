from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Twilio"
CAREERS_URL = "https://www.twilio.com/company/jobs"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("twilio")
