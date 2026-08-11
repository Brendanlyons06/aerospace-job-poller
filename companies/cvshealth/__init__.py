from ...filters import internships_in_us, swe_ml_jobs
from ..feeds import workday_jobs

COMPANY_NAME = "CVS Health"
CAREERS_URL = "https://jobs.cvshealth.com/"


def fetch_jobs() -> list[dict]:
    # CVS's only intern-typed Workday facet is "Pharmacy Intern (Trainee)"
    # (thousands of store roles); tech interns are typed Regular, so search
    # by keyword instead of faceting.
    return workday_jobs(
        "cvshealth",
        "CVS_Health_Careers",
        host="wd1",
        search_text="software engineer intern",
    )


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return swe_ml_jobs(internships_in_us(jobs))
