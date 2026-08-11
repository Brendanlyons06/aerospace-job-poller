from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Old Mission"
CAREERS_URL = "https://www.oldmissioncapital.com/careers/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("oldmissioncapital")
