from ..feeds import greenhouse_internships_us

COMPANY_NAME = "Box"
CAREERS_URL = "https://www.box.com/careers"


def fetch_jobs() -> list[dict]:
    # Box's Greenhouse board token is "boxinc", not "box".
    return greenhouse_internships_us("boxinc")
