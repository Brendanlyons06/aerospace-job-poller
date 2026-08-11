"""Citadel's open-opportunities page — a server-rendered WordPress listing.

The page carries every card in plain HTML (``data-position`` attribute plus
the detail link); there is no separate search API to call. Region lives only
in the title suffix — "(US)", "(Europe)", "(Asia)" — so US-ness is derived
from that marker. Cards without a region marker get no location and are
left for the caller's filter to drop.
"""

import html
import re

from ... import http

OPEN_OPPORTUNITIES_URL = "https://www.citadel.com/careers/open-opportunities/"

_CARD_RE = re.compile(
    r'<a[^>]*href="(?P<href>https://www\.citadel\.com/careers/details/[^"]+)"'
    r'[^>]*data-position="(?P<title>[^"]+)"[^>]*>'
)
_ALT_CARD_RE = re.compile(
    r'<a[^>]*data-position="(?P<title>[^"]+)"[^>]*'
    r'href="(?P<href>https://www\.citadel\.com/careers/details/[^"]+)"[^>]*>'
)
_REGION_RE = re.compile(r"\((US|Europe|Asia)\)\s*$")


def open_positions() -> list[dict]:
    """Every card on the open-opportunities page, normalized."""
    with http.session() as session:
        response = session.get(OPEN_OPPORTUNITIES_URL)
        response.raise_for_status()
        page = response.text

    jobs = []
    seen = set()
    for match in list(_CARD_RE.finditer(page)) + list(_ALT_CARD_RE.finditer(page)):
        url = match.group("href")
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        if not slug or slug in seen:
            continue
        seen.add(slug)
        # data-position is the exact display title, HTML-escaped ("&#8211;").
        title = html.unescape(match.group("title")).strip()
        region = _REGION_RE.search(title)
        if region:
            locations = ["United States"] if region.group(1) == "US" else [region.group(1)]
        else:
            locations = []
        jobs.append(
            {"id": slug, "title": title, "locations": locations, "url": url}
        )
    return jobs
