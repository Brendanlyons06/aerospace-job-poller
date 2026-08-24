from ...filters import is_internship_title
from ...profiles import role_title_filter
from ..feeds import greenhouse_jobs

COMPANY_NAME = "SpaceX"
CAREERS_URL = "https://www.spacex.com/careers/"


def fetch_jobs() -> list[dict]:
    """SpaceX aerospace/mechanical internships from its Greenhouse board.

    Every SpaceX site is in the United States (ITAR hiring), but the intern
    postings say "Flexible - Any SpaceX Site", which the generic US-location
    predicate can't recognize — so filter on title only here.
    """
    title_filter = role_title_filter(include_generic_engineering=True)
    return [
        job
        for job in greenhouse_jobs("spacex")
        if is_internship_title(job["title"]) and title_filter(job["title"])
    ]
