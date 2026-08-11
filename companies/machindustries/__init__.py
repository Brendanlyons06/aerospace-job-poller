from ...filters import is_internship_title, is_us_job
from ..feeds import ashby_jobs

COMPANY_NAME = "Mach Industries"
CAREERS_URL = "https://jobs.ashbyhq.com/mach"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("mach")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    # Mach posts one cross-discipline "Engineering Internship" per season and
    # types it FullTime in Ashby, so the structured employmentType filter in
    # ashby_internships_us misses it — match on the internship title instead.
    return [
        job for job in jobs
        if is_internship_title(job["title"]) and is_us_job(job)
    ]
