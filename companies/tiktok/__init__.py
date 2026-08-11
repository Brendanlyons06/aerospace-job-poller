"""TikTok US SWE/ML internships from the lifeattiktok search API."""

from ...filters import is_swe_ml_title
from . import client

COMPANY_NAME = "TikTok"
CAREERS_URL = "https://lifeattiktok.com/search?recruitment_id_list=202"

_US_COUNTRY = "United States of America"


def fetch_jobs() -> list[dict]:
    # Internship-ness comes from the API's structured recruitment type;
    # country from the structured location tree. Only the SWE/ML focus needs
    # the title.
    jobs = []
    for post in client.intern_postings():
        if post["country"] != _US_COUNTRY:
            continue
        if not is_swe_ml_title(post["title"]):
            continue
        locations = [post["city"]] if post["city"] else []
        jobs.append(
            {
                "id": post["id"],
                "title": post["title"],
                "locations": locations,
                "url": post["url"],
            }
        )
    return jobs
