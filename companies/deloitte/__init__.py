"""Deloitte US entry-level and internship feed adapter."""

from xml.etree import ElementTree

from ... import http

COMPANY_NAME = "Deloitte"
CAREERS_URL = "https://apply.deloitte.com/en_US/careers/SearchJobs?3_5_3=478&sort=relevancy"
FEED_URL = (
    "https://apply.deloitte.com/en_US/careers/SearchJobs/feed/"
    "?3_5_3=%5B%22478%22%5D&jobSort=relevancy"
    "&jobRecordsPerPage=100"
)


def fetch_jobs() -> list[dict]:
    """Read Deloitte's U.S. RSS feed with its Internship hire-type facet."""
    with http.session() as session:
        response = session.get(FEED_URL)
        response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    jobs = []
    for item in root.findall("./channel/item"):
        url = item.findtext("link")
        title = item.findtext("title")
        if not url or not title:
            continue
        job_id = url.rstrip("/").rsplit("/", 1)[-1]
        jobs.append({"id": job_id, "title": title, "locations": [], "url": url})
    return jobs
