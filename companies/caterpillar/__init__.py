import os

from ...filters import is_internship_title, is_swe_ml_title
from ...profiles import PROFILE_AEROSPACE, normalized_profile, role_title_filter
from ..feeds import official_page_jobs

COMPANY_NAME = "Caterpillar"
CAREERS_URL = "https://careers.caterpillar.com/en/jobs/"
SEARCH_URL = (
    "https://careers.caterpillar.com/en/jobs/"
    "?country=United+States+of+America&jobType=Intern+-+Temporary&pagesize=100"
)


def fetch_jobs() -> list[dict]:
    jobs = official_page_jobs(SEARCH_URL, r"/jobs/(r[0-9]+)/")
    predicate = role_title_filter(include_generic_engineering=True)
    include_broad_engineering = (
        normalized_profile(os.environ.get("JOB_POLLER_PROFILE"))
        == PROFILE_AEROSPACE
    )
    return [
        job for job in jobs
        if is_internship_title(job["title"])
        and (
            predicate(job["title"])
            or (
                include_broad_engineering
                and "engineering" in job["title"].lower()
                and not is_swe_ml_title(job["title"])
            )
        )
    ]
