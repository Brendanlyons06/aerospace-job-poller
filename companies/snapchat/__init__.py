from ..feeds import official_page_jobs, technical_internships

COMPANY_NAME = "Snap Inc."
CAREERS_URL = "https://careers.snap.com/jobs"


def fetch_jobs() -> list[dict]:
    """Read job cards rendered by Snap's own careers page."""
    return official_page_jobs(CAREERS_URL, r"/job\?id=([A-Za-z0-9]+)")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
