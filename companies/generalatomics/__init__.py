from ...profiles import role_title_filter
from ..feeds import brassring_internships_us

COMPANY_NAME = "General Atomics Aeronautical Systems"
CAREERS_URL = "https://www.ga.com/careers/early-career"


def fetch_jobs() -> list[dict]:
    # The official General Atomics board labels current aerospace and
    # mechanical internships as the parent "General Atomics" department,
    # rather than the narrower GA-ASI department name.  Keep the title-based
    # engineering filter, but do not discard those valid parent-company roles.
    return brassring_internships_us(
        "25539",
        "5310",
        title_filter=role_title_filter(include_generic_engineering=True),
    )
