from ..feeds import technical_internships, workday_jobs

COMPANY_NAME = "Micron"
CAREERS_URL = "https://careers.micron.com/"


def fetch_jobs() -> list[dict]:
    # This is the Intern - Regular facet exposed by Micron's official
    # Workday-backed careers search; it avoids downloading thousands of
    # non-intern manufacturing roles.
    return workday_jobs(
        "micron",
        "External",
        host="wd1",
        search_text="",
        applied_facets={
            "workerSubType": ["bff7a31dbdd3016722f3aeb41a01cf81"],
        },
    )


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
