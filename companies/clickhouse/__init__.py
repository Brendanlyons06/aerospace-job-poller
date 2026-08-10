from ..feeds import ashby_jobs, technical_internships

COMPANY_NAME = "ClickHouse"
CAREERS_URL = "https://jobs.ashbyhq.com/clickhouse"


def fetch_jobs() -> list[dict]:
    return ashby_jobs("clickhouse")


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
