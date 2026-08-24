import os

from ...profiles import PROFILE_AEROSPACE, normalized_profile, role_title_filter
from ..feeds import ashby_internships_us

COMPANY_NAME = "Starpath"
CAREERS_URL = "https://starpath.space/careers"


def _target_title(title: str) -> bool:
    return role_title_filter(include_generic_engineering=True)(title) or (
        normalized_profile(os.environ.get("JOB_POLLER_PROFILE"))
        == PROFILE_AEROSPACE
        and title.strip().lower() == "intern/associate engineer - all roles"
    )


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("starpath.space", title_filter=_target_title)
