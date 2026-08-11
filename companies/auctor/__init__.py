from ...filters import is_internship_title, is_swe_ml_title, is_us_job
from ..feeds import ashby_jobs

COMPANY_NAME = "Auctor"
CAREERS_URL = "https://jobs.ashbyhq.com/auctor"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("auctor")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    # Auctor types its internships FullTime in Ashby (like Mach), so the
    # structured employmentType filter in ashby_internships_us misses them —
    # match on the internship title instead.
    return [
        job for job in jobs
        if is_internship_title(job["title"])
        and is_swe_ml_title(job["title"])
        and is_us_job(job)
    ]
