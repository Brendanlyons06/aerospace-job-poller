"""Two Sigma's Avature-hosted careers site (careers.twosigma.com).

The OpenRoles listing server-renders every job card as a plain anchor whose
URL embeds location and title slugs and ends in the stable numeric job id:

    /careers/JobDetail/<City-...-Country-Title-slug>/<id>

Pagination is ``?jobRecordsPerPage=10&jobOffset=N``; the site ignores larger
page sizes, so this walks offsets of 10 until a page adds nothing new. The
``/careers/OpenRoles/feed/`` RSS route exists but only carries the 20 newest
roles, which can miss older internship postings — don't switch to it.
"""

import html
import re

from ... import http

LISTING_URL = "https://careers.twosigma.com/careers/OpenRoles/"

_CARD_RE = re.compile(
    r'<a[^>]*href="(?P<url>https://careers\.twosigma\.com/careers/JobDetail/'
    r'[^"]+/(?P<id>\d+))"[^>]*>(?P<body>.*?)</a>',
    re.S,
)
_MAX_PAGES = 50


def open_roles() -> list[dict]:
    """Every job card across the paginated OpenRoles listing."""
    jobs: dict[str, dict] = {}
    with http.session() as session:
        for page in range(_MAX_PAGES):
            response = session.get(
                LISTING_URL,
                params={"jobRecordsPerPage": 10, "jobOffset": page * 10},
            )
            response.raise_for_status()
            before = len(jobs)
            for match in _CARD_RE.finditer(response.text):
                job_id = match.group("id")
                title = re.sub(r"<[^>]+>", " ", match.group("body"))
                title = re.sub(r"\s+", " ", html.unescape(title)).strip()
                # Each card renders two anchors to the same URL — the titled
                # one and a "View role" button; keep the real title.
                if not title or title.lower() == "view role":
                    continue
                jobs.setdefault(
                    job_id,
                    {
                        "id": job_id,
                        "title": title,
                        # The slug spells out the location; the US marker is
                        # all the poller's filter needs.
                        "locations": (
                            ["United States"]
                            if "united-states" in match.group("url").lower()
                            else []
                        ),
                        "url": match.group("url"),
                    },
                )
            if len(jobs) == before:
                break
    return list(jobs.values())
