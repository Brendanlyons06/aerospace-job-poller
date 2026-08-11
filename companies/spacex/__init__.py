from ...filters import is_internship_title, is_swe_ml_title
from ..feeds import greenhouse_jobs

COMPANY_NAME = "SpaceX"
CAREERS_URL = "https://www.spacex.com/careers/"


def fetch_jobs() -> list[dict]:
    """SpaceX internships from its Greenhouse board, without the US check.

    Every SpaceX site is in the United States (ITAR hiring), but the intern
    postings say "Flexible - Any SpaceX Site", which the generic US-location
    predicate can't recognize — so filter on title only here.
    """
    return [
        job
        for job in greenhouse_jobs("spacex")
        if is_internship_title(job["title"]) and is_swe_ml_title(job["title"])
    ]
