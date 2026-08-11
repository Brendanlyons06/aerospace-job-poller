"""D. E. Shaw's careers site — jobs ship inside the page's Next.js payload.

www.deshaw.com/careers server-renders a ``__NEXT_DATA__`` JSON blob whose
``pageProps`` carries ``internships`` and ``regularJobs`` outright, so there
is no separate search API to call and nothing token-like to rot. If parsing
starts failing, the site was rebuilt — re-inspect the page for where the
job arrays moved.
"""

import json
import re

from ... import http

CAREERS_URL = "https://www.deshaw.com/careers"

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S
)


def careers_page_props() -> dict:
    """The ``pageProps`` object embedded in the careers page."""
    with http.session() as session:
        response = session.get(CAREERS_URL)
        response.raise_for_status()
        match = _NEXT_DATA_RE.search(response.text)
    if not match:
        raise ValueError("could not find __NEXT_DATA__ on the D. E. Shaw careers page")
    return json.loads(match.group(1))["props"]["pageProps"]


def internships() -> list[dict]:
    """Normalized internship postings from the embedded page data."""
    jobs = []
    for posting in careers_page_props().get("internships", []):
        job_id = posting.get("id")
        title = posting.get("displayName", "")
        if not job_id or not title:
            continue
        slug = (posting.get("data") or {}).get("jobUrl")
        jobs.append(
            {
                "id": str(job_id),
                "title": title,
                "locations": [
                    office["name"]
                    for office in posting.get("office") or []
                    if office.get("name")
                ],
                "url": f"{CAREERS_URL}/{slug}" if slug else CAREERS_URL,
            }
        )
    return jobs
