from ..feeds import ashby_internships_us

COMPANY_NAME = "Supabase"
CAREERS_URL = "https://jobs.ashbyhq.com/supabase"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("supabase")
