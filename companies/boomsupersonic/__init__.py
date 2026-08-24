import os
import re

from ...filters import is_internship_title
from ...profiles import PROFILE_AEROSPACE, normalized_profile, role_title_filter
from ..feeds import official_page_jobs

COMPANY_NAME = "Boom Supersonic"
CAREERS_URL = "https://boomsupersonic.com/careers"


def _target_title(title: str) -> bool:
    return role_title_filter(include_generic_engineering=True)(title) or (
        normalized_profile(os.environ.get("JOB_POLLER_PROFILE"))
        == PROFILE_AEROSPACE
        and "engineering and tech internship" in title.lower()
    )


def fetch_jobs() -> list[dict]:
    jobs = official_page_jobs(
        CAREERS_URL,
        r"/boom-supersonic/jobs/([0-9a-f-]+)",
    )
    for job in jobs:
        match = re.match(
            r"^(.*\bInternship)\s+([^,]+,\s+[A-Za-z ]+)$",
            job["title"],
            re.IGNORECASE,
        )
        if match:
            job["title"] = match.group(1)
            job["locations"] = [match.group(2)]
    return [
        job for job in jobs
        if is_internship_title(job["title"]) and _target_title(job["title"])
    ]
