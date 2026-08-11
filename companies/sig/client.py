"""SIG (Susquehanna) careers — a Jibe/iCIMS site with a public JSON API.

careers.sig.com serves its own listing JSON at ``/api/jobs?page=N`` (about
20 records per page, ``totalCount`` for the stop condition). Records carry a
stable iCIMS ``req_id``, structured ``city``/``state``/``country``, and a
first-party ``category`` facet whose " Interns + Co-ops" value (note the
leading space) marks the internship program — no title guessing needed.

The hosted pages behind ``/search-results`` redirect-loop for non-browser
clients; the JSON API does not, so stay on it.
"""

from ... import http

API_URL = "https://careers.sig.com/api/jobs"
JOB_URL = "https://careers.sig.com/job/{req_id}"

INTERN_CATEGORY = "interns + co-ops"


def all_jobs() -> list[dict]:
    """Every record in the careers API, with pagination."""
    records = []
    page = 1
    while True:
        payload = http.get_json(API_URL, params={"page": page})
        batch = payload.get("jobs", [])
        records.extend(
            job["data"] for job in batch if isinstance(job.get("data"), dict)
        )
        if not batch or len(records) >= int(payload.get("totalCount") or 0):
            break
        page += 1
    return records


def intern_postings() -> list[dict]:
    """Normalized postings in SIG's own internship category."""
    jobs = []
    seen = set()
    for record in all_jobs():
        categories = {
            str(category).strip().lower()
            for category in record.get("category") or []
        }
        if INTERN_CATEGORY not in categories:
            continue
        req_id = record.get("req_id") or record.get("slug")
        if not req_id or str(req_id) in seen:
            continue
        seen.add(str(req_id))
        location = ", ".join(
            part
            for part in (record.get("city"), record.get("state"), record.get("country"))
            if part
        )
        jobs.append(
            {
                "id": str(req_id),
                "title": record.get("title", ""),
                "locations": [location] if location else [],
                "country": record.get("country"),
                "url": JOB_URL.format(req_id=req_id),
            }
        )
    return jobs
