from ..feeds import ashby_internships_us

COMPANY_NAME = "ClickHouse"
CAREERS_URL = "https://jobs.ashbyhq.com/clickhouse"


def fetch_jobs() -> list[dict]:
    return ashby_internships_us("clickhouse")
