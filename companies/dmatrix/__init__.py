from ..feeds import ashby_internships_us

COMPANY_NAME = "d-Matrix"
CAREERS_URL = "https://www.d-matrix.ai/careers/"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("d-matrix")
