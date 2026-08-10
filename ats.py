"""Adapters for the hosted job-board platforms most companies actually use.

Before reverse-engineering a career site's private API from a HAR capture
(see AGENTS.md), check whether the company just runs Greenhouse or Lever —
a large share of tech companies do. Both expose a public, unauthenticated,
documented-enough JSON endpoint, which turns a company adapter into four
lines with no HAR, no CSRF token, and nothing that rots when the site's
frontend is rebuilt.

    from ...ats import greenhouse

    COMPANY_NAME = "Anthropic"

    def fetch_jobs() -> list[dict]:
        return greenhouse("anthropic")

Each function returns the standard shape watch.py expects — see
companies/README.md:
    {"id": str, "title": str, "locations": list[str], "url": str}

## Finding the board token

It's the company slug in their job board's URL, not a secret:
  - Greenhouse: boards.greenhouse.io/<token> or job-boards.greenhouse.io/<token>
  - Lever:      jobs.lever.co/<token>
Career pages that embed listings in an iframe usually reveal it in the
iframe `src`. Verify with `python -m careers.check <company>` before
committing the adapter.
"""

from . import http
from .filters import is_us_location

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
LEVER_URL = "https://api.lever.co/v0/postings/{token}?mode=json"


def greenhouse(board_token: str) -> list[dict]:
    """Every open posting on a company's Greenhouse board."""
    payload = http.get_json(GREENHOUSE_URL.format(token=board_token))
    jobs = []
    for job in payload.get("jobs", []):
        # Greenhouse's id is a stable numeric posting id — exactly the
        # dedup key jobs.db wants. `location` is occasionally null on
        # postings that never had one set.
        location = (job.get("location") or {}).get("name")
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": [location] if location else [],
                "url": job["absolute_url"],
            }
        )
    return jobs


def lever(
    board_token: str,
    *,
    commitment: str | None = None,
    country: str | None = None,
) -> list[dict]:
    """Every open posting on a company's Lever board.

    ``commitment`` matches Lever's first-party employment-type category, such
    as ``"Intern"``.  Lever's public postings endpoint returns the full
    board even when the hosted page displays this filter, so select the
    category from the API record here rather than inferring it from a mutable
    job title. ``country="United States"`` validates Lever's client-side
    location category against the normalized posting locations.
    """
    postings = http.get_json(LEVER_URL.format(token=board_token))
    jobs = []
    for job in postings:
        categories = job.get("categories") or {}
        if commitment is not None and categories.get("commitment") != commitment:
            continue
        # allLocations is the multi-location list; older postings only have
        # the single `location` string.
        locations = categories.get("allLocations")
        if not locations:
            single = categories.get("location")
            locations = [single] if single else []
        if country == "United States" and not any(
            is_us_location(location) for location in locations
        ):
            continue
        jobs.append(
            {
                "id": job["id"],  # Lever uses a stable UUID
                "title": job["text"],
                "locations": list(locations),
                "url": job["hostedUrl"],
            }
        )
    return jobs
