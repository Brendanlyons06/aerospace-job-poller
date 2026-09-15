from ...filters import is_internship_title, is_us_job
from ..feeds import greenhouse_jobs

COMPANY_NAME = "Mach Industries"
CAREERS_URL = "https://machindustries.com/careers"


def fetch_jobs() -> list[dict]:
    # Mach moved its public board from Ashby to Greenhouse in September 2026.
    # The old Ashby posting API now returns HTTP 404, while the official
    # careers page links to this Greenhouse board.
    return greenhouse_jobs("machindustries")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    # Mach posts one cross-discipline "Engineering Internship" per season and
    # types it FullTime in Ashby, so the structured employmentType filter in
    # ashby_internships_us misses it — match on the internship title instead.
    return [
        job for job in jobs
        if is_internship_title(job["title"]) and is_us_job(job)
    ]
