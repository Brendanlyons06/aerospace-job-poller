from ..feeds import ibm_jobs

COMPANY_NAME = "IBM"
CAREERS_URL = "https://www.ibm.com/careers/search?q=intern"


def fetch_jobs() -> list[dict]:
    return ibm_jobs()
