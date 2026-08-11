"""SIG (Susquehanna) US software internships from its careers API."""

from ...filters import is_swe_ml_title
from . import client

COMPANY_NAME = "SIG"
CAREERS_URL = "https://careers.sig.com/"


def fetch_jobs() -> list[dict]:
    # Internship-ness and country come from the API's structured fields;
    # only the SWE/ML focus needs the title.
    return [
        {key: job[key] for key in ("id", "title", "locations", "url")}
        for job in client.intern_postings()
        if job.get("country") == "United States" and is_swe_ml_title(job["title"])
    ]
