from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Netskope"
CAREERS_URL = "https://job-boards.greenhouse.io/netskope"


def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("netskope")
