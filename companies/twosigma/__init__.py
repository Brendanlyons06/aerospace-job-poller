"""Two Sigma internships from its Avature careers listing."""

from ...filters import internships_in_us
from . import client

COMPANY_NAME = "Two Sigma"
CAREERS_URL = "https://careers.twosigma.com/careers/OpenRoles/"


def fetch_jobs() -> list[dict]:
    return internships_in_us(client.open_roles())
