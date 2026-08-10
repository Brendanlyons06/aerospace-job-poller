from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Twitch"
CAREERS_URL = "https://job-boards.greenhouse.io/twitch"


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("twitch")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
