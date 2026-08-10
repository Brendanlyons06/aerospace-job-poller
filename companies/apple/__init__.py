"""Apple's student internship search board."""

from html import unescape
from html.parser import HTMLParser
import re

from ... import http
from ...filters import is_us_job

COMPANY_NAME = "Apple"
SEARCH_URL = "https://jobs.apple.com/en-us/search"


class _JobParser(HTMLParser):
    """Extract the server-rendered job cards from Apple's search results."""

    def __init__(self) -> None:
        super().__init__()
        self.jobs: list[dict] = []
        self._anchor: dict | None = None
        self._location: str | None = None
        self._text: list[str] = []
        self._in_location = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "/details/" in attrs.get("href", ""):
            self._anchor = {"href": attrs["href"]}
            self._text = []
        if attrs.get("id", "").startswith("search-store-name-container-"):
            self._in_location = True
            self._text = []

    def handle_data(self, data):
        if self._anchor is not None:
            self._text.append(data)
        if self._in_location:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._anchor is not None:
            self._anchor["title"] = " ".join("".join(self._text).split())
            self._text = []
        if tag == "span" and self._in_location:
            self._location = " ".join("".join(self._text).split())
            self._in_location = False
            self._text = []
        if tag == "li" and self._anchor is not None:
            href = self._anchor["href"]
            match = re.search(r"/details/(\\d+-\\d+)/", href)
            if match and self._anchor.get("title"):
                self.jobs.append(
                    {
                        "id": match.group(1),
                        "title": unescape(self._anchor["title"]),
                        "locations": [self._location] if self._location else [],
                        "url": "https://jobs.apple.com" + href,
                    }
                )
            self._anchor = None
            self._location = None


def fetch_jobs() -> list[dict]:
    """Return Apple internship postings from all result pages."""
    jobs: list[dict] = []
    for page in range(1, 20):
        with http.session() as session:
            response = session.get(
                SEARCH_URL,
                params={
                    "team": "internships-STDNT-INTRN",
                    "location": "united-states-USA",
                    "page": page,
                },
            )
        response.raise_for_status()
        page_jobs = []
        for block in re.findall(
            r'<div id="search-search-job-title-[^"]+".*?</li>',
            response.text,
            re.DOTALL,
        ):
            link = re.search(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)
            location = re.search(
                r'id="search-store-name(?:-container)?-\d+">(.*?)</span>',
                block,
                re.DOTALL,
            )
            if not link:
                continue
            match = re.search(r"/details/(\d+-\d+)/", link.group(1))
            if not match:
                continue
            page_jobs.append(
                {
                    "id": match.group(1),
                    "title": re.sub(r"\s+", " ", unescape(link.group(2))).strip(),
                    "locations": [
                        re.sub(r"\s+", " ", unescape(location.group(1))).strip()
                    ]
                    if location
                    else [],
                    "url": "https://jobs.apple.com" + link.group(1),
                }
            )
        if not page_jobs:
            break
        jobs.extend(page_jobs)
        if len(page_jobs) < 20:
            break
    return jobs


def filter_jobs(jobs: list[dict]) -> list[dict]:
    """The request already uses Apple's Internship team; keep U.S. results."""
    return [job for job in jobs if is_us_job(job)]
