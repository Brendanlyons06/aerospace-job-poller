"""Shield AI jobs from the Lever board linked by its official careers page."""

from ...ats import lever
from ..feeds import technical_internships

COMPANY_NAME = "Shield AI"
CAREERS_URL = "https://shield.ai/careers/"


def fetch_jobs() -> list[dict]:
    return lever("shieldai")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
