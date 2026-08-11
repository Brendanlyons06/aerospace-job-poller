"""Rippling's careers board (Rippling runs its own ATS) via its Algolia index.

www.rippling.com/careers/open-roles (where ats.rippling.com/rippling/jobs
redirects) renders nothing server-side; the browser queries a public,
search-only Algolia index instead. The application id and search key below
ship in the site's JS bundle (`_next/static/chunks/pages/_app-*.js`) — they
are client-side by design, not secrets, but they will rot if Rippling
rotates them. If queries start failing with 403, re-extract both constants
from the current `_app` bundle (search it for a 32-hex string with a
10-character uppercase id nearby).

Each Algolia hit is one (job, location) pair — `objectID` is
`<jobId>__<location-slug>` — so the same posting appears once per location
and callers must merge on the stable `jobId` field.
"""

from ... import http

ALGOLIA_APP_ID = "6FNAX3TBEF"
ALGOLIA_SEARCH_KEY = "416caa4690f002ff6fe4a2097623640b"  # search-only, public
ALGOLIA_INDEX = "careers_en-US_production"

_QUERY_URL = (
    f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"
)
_PAGE_SIZE = 100


def search_hits(query: str = "") -> list[dict]:
    """Every (job, location) hit in the careers index for ``query``."""
    hits = []
    page = 0
    with http.session() as session:
        while True:
            response = session.post(
                _QUERY_URL,
                headers={
                    "x-algolia-application-id": ALGOLIA_APP_ID,
                    "x-algolia-api-key": ALGOLIA_SEARCH_KEY,
                },
                json={
                    "params": f"query={query}&hitsPerPage={_PAGE_SIZE}&page={page}"
                },
            )
            response.raise_for_status()
            payload = response.json()
            hits.extend(payload.get("hits", []))
            page += 1
            if page >= int(payload.get("nbPages") or 0):
                break
    return hits
