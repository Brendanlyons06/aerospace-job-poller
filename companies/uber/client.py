"""Uber's job board (jobs.uber.com) — Oracle Recruiting Cloud underneath.

The site's own login link exposes the Oracle CE tenant
(``iaziqy.fa.ocs.oraclecloud.com``), whose anonymous REST endpoint
``recruitingCEJobRequisitions`` serves the same requisitions the board
renders. Quirk: the response reports ``TotalJobsCount`` but leaves
``requisitionList`` empty unless both the ``expand`` parameter and the
``facetsList`` finder argument are present — keep them even though they look
optional. ``Id`` is the stable requisition number shown in job URLs.
"""

from ... import http

TENANT = "https://iaziqy.fa.ocs.oraclecloud.com"
API_URL = f"{TENANT}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
SITE_NUMBER = "CX_1"
JOB_URL = "https://jobs.uber.com/en/jobs/{req_id}/"

_FACETS = (
    "LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;"
    "ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS"
)
_PAGE_SIZE = 100


def search_requisitions(keyword: str = "intern") -> list[dict]:
    """Every requisition matching ``keyword``, normalized to the job dict."""
    jobs = []
    seen = set()
    offset = 0
    with http.session() as session:
        while True:
            finder = (
                f"findReqs;siteNumber={SITE_NUMBER},facetsList={_FACETS},"
                f'limit={_PAGE_SIZE},keyword="{keyword}",offset={offset},'
                "sortBy=POSTING_DATES_DESC"
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
                    }
                )
            offset += len(page)
            if not page or offset >= int(item.get("TotalJobsCount") or 0):
                break
    return jobs
