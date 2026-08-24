from ...profiles import role_title_filter
from ..feeds import impulse_space_internships_us

COMPANY_NAME = "Impulse Space"
CAREERS_URL = "https://www.impulsespace.com/careers"


def fetch_jobs() -> list[dict]:
    return impulse_space_internships_us(title_filter=role_title_filter())
