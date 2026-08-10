from ..feeds import ashby_internships_us

COMPANY_NAME = "Notion"
CAREERS_URL = "https://www.notion.com/careers"

def fetch_jobs() -> list[dict]:
    return ashby_internships_us("notion")
