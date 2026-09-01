from ...profiles import role_title_filter
from ..feeds import brassring_internships_us

COMPANY_NAME = "General Atomics Aeronautical Systems"
CAREERS_URL = "https://www.ga.com/careers/early-career"


def fetch_jobs() -> list[dict]:
    return brassring_internships_us(
        "25539",
        "5310",
        department_contains="General Atomics Aeronautical Systems",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
