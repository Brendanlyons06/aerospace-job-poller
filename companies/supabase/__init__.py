from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "Supabase"
CAREERS_URL = "https://jobs.ashbyhq.com/supabase"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("supabase")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
