"""PwC US technical-internship search adapter."""

import html
import re

from ... import http
from ..feeds import technical_internships

COMPANY_NAME = "PwC"
CAREERS_URL = "https://jobs.us.pwc.com/search-jobs?k=intern"

_JOB = re.compile(
    r'<a\b[^>]*\bclass="[^"]*search-results-list__job-link[^"]*"'
    r'[^>]*\bhref="(?P<href>/job/[^"]+)"[^>]*\bdata-job-id="(?P<id>[^"]+)"'
    r'[^>]*>(?P<title>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)


def fetch_jobs() -> list[dict]:
    """Read PwC's official internship search results, without related-job cards."""
    with http.session() as session:
        response = session.get(CAREERS_URL)
        response.raise_for_status()
    return [
        {
            "id": match.group("id"),
            "title": re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", match.group("title")))).strip(),
            "locations": [],
            "url": "https://jobs.us.pwc.com" + html.unescape(match.group("href")),
        }
        for match in _JOB.finditer(response.text)
    ]


def filter_jobs(jobs: list[dict]) -> list[dict]:
    return technical_internships(jobs)
