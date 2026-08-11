from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Abnormal AI"
CAREERS_URL = "https://abnormal.ai/careers"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("abnormalsecurity")
