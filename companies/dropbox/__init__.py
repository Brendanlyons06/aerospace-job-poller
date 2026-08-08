from ..feeds import greenhouse_jobs, technical_internships

COMPANY_NAME = "Dropbox"
CAREERS_URL = "https://jobs.dropbox.com/"

def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("dropbox")

def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
