from ..feeds import technical_internships, workday_jobs

COMPANY_NAME = "Intel"
CAREERS_URL = "https://jobs.intel.com/en/search-jobs/intern"


def fetch_jobs() -> list[dict]:
    return workday_jobs("intel", "External", host="wd1")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
