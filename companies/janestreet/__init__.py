from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Jane Street"
CAREERS_URL = "https://www.janestreet.com/join-jane-street/"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("janestreet")
