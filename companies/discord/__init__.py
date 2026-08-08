from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Discord"
CAREERS_URL = "https://discord.com/jobs"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("discord")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
