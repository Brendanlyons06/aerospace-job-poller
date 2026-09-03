"""Honeywell's Oracle Recruiting Cloud careers feed.

Honeywell's official careers site serves requisitions from its public Oracle
Candidate Experience API.  Its keyword search currently returns broad
matches, so this client pages the board deterministically and leaves the
strict internship/discipline filtering to the adapter.
"""

from ... import http

TENANT = "https://ibqbjb.fa.ocs.oraclecloud.com"
API_URL = f"{TENANT}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
SITE_NUMBER = "CX_1"
JOB_URL = "https://careers.honeywell.com/en/sites/Honeywell/job/{req_id}"

_FACETS = (
    "LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;"
    "ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS"
)
_PAGE_SIZE = 100


def search_requisitions() -> list[dict]:
    """Return the public Honeywell requisitions with stable job IDs."""
    jobs = []
    seen = set()
    offset = 0
    # The board is paginated; avoid multiplying the standard retry budget by
    # every page. A transient source failure is isolated and retried by the
    # next hourly poll.
    with http.session(retries=0) as session:
        while True:
            finder = (
                f"findReqs;siteNumber={SITE_NUMBER},facetsList={_FACETS},"
                f"limit={_PAGE_SIZE},offset={offset},sortBy=POSTING_DATES_DESC"
            )
            response = session.get(
                API_URL,
                params={
                    "onlyData": "true",
                    "expand": "requisitionList.secondaryLocations",
                    "finder": finder,
                },
                headers={"accept": "application/json"},
            )
            response.raise_for_status()
            item = (response.json().get("items") or [{}])[0]
            page = item.get("requisitionList") or []
            for req in page:
                req_id = req.get("Id")
                if not req_id or str(req_id) in seen:
                    continue
                seen.add(str(req_id))
                locations = [
                    location
                    for location in [req.get("PrimaryLocation")]
                    + [
                        secondary.get("Name")
                        for secondary in req.get("secondaryLocations") or []
                    ]
                    if location
                ]
                jobs.append(
                    {
                        "id": str(req_id),
                        "title": req.get("Title", ""),
                        "locations": locations,
                        "url": JOB_URL.format(req_id=req_id),
                        "posted_at": req.get("PostedDate"),
                    }
                )
            offset += len(page)
            if not page or offset >= int(item.get("TotalJobsCount") or 0):
                break
    return jobs
