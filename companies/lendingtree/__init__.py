from ..feeds import greenhouse_internships_us

COMPANY_NAME = "LendingTree"
CAREERS_URL = "https://job-boards.greenhouse.io/lendingtree"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("lendingtree")
