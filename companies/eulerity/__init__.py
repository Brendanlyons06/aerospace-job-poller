import re

from ...filters import is_internship_title, is_us_job
from ..feeds import greenhouse_jobs

COMPANY_NAME = "Eulerity"
CAREERS_URL = "https://www.eulerity.com/careers"

# Eulerity titles its SWE internships "<platform> Developer Intern" (e.g.
# "Mobile iOS Developer Intern"), which the shared SWE/ML regex misses.
DEV_RE = re.compile(r"\b(?:developer|engineer)\b", re.IGNORECASE)


def fetch_jobs() -> list[dict]:
    return greenhouse_jobs("eulerity")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return [
        job for job in jobs
        if is_internship_title(job["title"])
        and DEV_RE.search(job["title"])
        and is_us_job(job)
    ]
