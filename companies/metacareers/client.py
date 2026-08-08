"""
Recreates the MetaCareers job-search request captured in
www.metacareers.com.har, alongside this file (HAR entry 21:
CareersJobSearchResultsV2DataQuery).

Flow (mirrors what the browser does):
1. GET /jobsearch/ to pick up cookies and scrape the `lsd` CSRF token embedded
   in the page HTML.
2. POST /graphql with that token plus the persisted-query `doc_id` for
   CareersJobSearchResultsV2DataQuery and a `variables` JSON blob describing
   the filters (roles, offices, teams, search text, ...).

doc_id is a persisted-query id tied to Meta's current frontend build — if this
starts 404ing or erroring, re-capture a HAR and grab the new doc_id/friendly
name pair from a fresh /graphql POST.
"""

import json
import re
import sys

import requests

from ... import http

BASE = "https://www.metacareers.com"
JOBSEARCH_URL = f"{BASE}/jobsearch/"
GRAPHQL_URL = f"{BASE}/graphql"

DOC_ID = "27129360303422352"  # CareersJobSearchResultsV2DataQuery, captured 2026-08-05

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)


def get_lsd_token(session: requests.Session) -> str:
    # Anonymous requests need a `datr` cookie before /jobsearch/ will render
    # (a bare GET to /jobsearch/ with no prior visit gets a 400 app error), so
    # hit the landing page first, same as a real browser would.
    common_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": USER_AGENT,
    }

    landing = session.get(BASE + "/", headers={**common_headers, "sec-fetch-site": "none"})
    landing.raise_for_status()

    resp = session.get(
        JOBSEARCH_URL,
        headers={**common_headers, "sec-fetch-site": "same-origin", "referer": BASE + "/"},
    )
    resp.raise_for_status()
    match = re.search(r'"LSD"[^}]{0,80}"token"\s*:\s*"([A-Za-z0-9_-]+)"', resp.text)
    if not match:
        raise RuntimeError("could not find lsd token on jobsearch page")
    return match.group(1)


def search_jobs(
    roles=None,
    q=None,
    offices=None,
    divisions=None,
    teams=None,
    results_per_page=None,
):
    # http.session() rather than requests.Session() so both calls below carry
    # a timeout — watch.py fetches companies on a thread pool it can't
    # interrupt, so an untimed request here would strand a worker.
    session = http.session()
    lsd = get_lsd_token(session)

    variables = {
        "search_input": {
            "q": q,
            "divisions": divisions or [],
            "offices": offices or [],
            "roles": roles or [],
            "leadership_levels": [],
            "saved_jobs": [],
            "saved_searches": [],
            "sub_teams": [],
            "teams": teams or [],
            "is_leadership": False,
            "is_remote_only": False,
            "sort_by_new": False,
            "results_per_page": results_per_page,
        },
        "viewasUserID": None,
        "isLoggedIn": False,
    }

    data = {
        "av": "0",
        "__user": "0",
        "__a": "1",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "CareersJobSearchResultsV2DataQuery",
        "server_timestamps": "true",
        "doc_id": DOC_ID,
        "variables": json.dumps(variables),
        "lsd": lsd,
    }

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": BASE,
        "referer": JOBSEARCH_URL,
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": USER_AGENT,
        "x-fb-friendly-name": "CareersJobSearchResultsV2DataQuery",
        "x-fb-lsd": lsd,
    }

    resp = session.post(GRAPHQL_URL, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    roles = sys.argv[1:] or None
    result = search_jobs(roles=roles)
    jobs = result["data"]["job_search_with_featured_jobs_v2"]["all_jobs"]
    print(f"{len(jobs)} jobs" + (f" (roles={roles})" if roles else ""))
    for job in jobs:
        print(f"- {job['title']} — {', '.join(job['locations'])}")
