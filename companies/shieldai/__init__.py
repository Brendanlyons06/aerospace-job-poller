"""Shield AI jobs from the Lever board linked by its official careers page."""

from ...ats import lever
COMPANY_NAME = "Shield AI"
CAREERS_URL = "https://shield.ai/careers/"


def fetch_jobs() -> list[dict]:
    """Match Shield AI's official Lever ``commitment=Intern`` view."""
    return lever("shieldai", commitment="Intern", country="United States")
