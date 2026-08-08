"""Small read-only feed helpers used by company-specific adapters.

Each adapter still owns its official careers URL, board identifier, and
filter. These helpers only normalize the public JSON shape returned by the
careers sites' own listing feeds.
"""

import html
import json
import re
from urllib.parse import unquote, urljoin

from .. import http


def official_page_jobs(
    careers_url: str,
    link_pattern: str,
    *,
    listing_url: str | None = None,
) -> list[dict]:
    """Extract jobs rendered directly by a company's official careers page.

    ``link_pattern`` must contain one capture group for the stable job ID.
    This deliberately reads the company page, rather than an ATS vendor's
    listing API.  ``listing_url`` is useful where the official page links out
    to the ATS only for the application form: alerts should still take the
    user back to the company's own careers site.
    """
    with http.session() as session:
        response = session.get(careers_url)
        response.raise_for_status()
        page = response.text

    anchor = re.compile(
        r'<a\b[^>]*\bhref=["\'](?P<href>[^"\']+)["\'][^>]*>'
        r'(?P<body>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    pattern = re.compile(link_pattern, re.IGNORECASE)
    jobs = []
    seen = set()
    for match in anchor.finditer(page):
        href = html.unescape(match.group("href")).replace("\\u0026", "&")
        id_match = pattern.search(href)
        if not id_match:
            continue
        job_id = id_match.group(1)
        if job_id in seen:
            continue
        title = re.sub(r"<[^>]+>", " ", match.group("body"))
        title = re.sub(r"\s+", " ", html.unescape(title)).strip()
        # Inline CSS occasionally appears before the visible anchor text.
        title = re.sub(r"(?:\.[\w-]+\s*\{[^{}]*\}\s*)+", "", title).strip()
        if not title:
            continue
        seen.add(job_id)
        jobs.append(
            {
                "id": str(job_id),
                "title": title,
                "locations": [],
                "url": listing_url or urljoin(careers_url, href),
            }
        )
    return jobs


def greenhouse_jobs(board: str, *, content: bool = False) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    if content:
        url += "?content=true"
    payload = http.get_json(url)
    jobs = []
    for job in payload.get("jobs", []):
        location = (job.get("location") or {}).get("name")
        locations = [location] if location else []
        for metadata in (job.get("metadata") or []):
            if metadata.get("name") in {"Job Posting Location", "Location"}:
                value = metadata.get("value")
                if isinstance(value, list):
                    locations.extend(v for v in value if isinstance(v, str))
                elif isinstance(value, str):
                    locations.append(value)
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": list(dict.fromkeys(locations)),
                "url": job["absolute_url"],
            }
        )
    return jobs


def workday_jobs(
    tenant: str,
    site: str,
    *,
    search_text: str = "intern",
    host: str = "wd5",
    applied_facets: dict | None = None,
) -> list[dict]:
    """Read the public Workday search feed used by an official careers site."""
    endpoint = (
        f"https://{tenant}.{host}.myworkdayjobs.com/wday/cxs/"
        f"{tenant}/{site}/jobs"
    )
    detail_base = f"https://{tenant}.{host}.myworkdayjobs.com/en-US/{site}"
    jobs = []
    offset = 0
    page_size = 20
    with http.session() as session:
        while True:
            response = session.post(
                endpoint,
                json={
                    "appliedFacets": applied_facets or {},
                    "limit": page_size,
                    "offset": offset,
                    "searchText": search_text,
                },
            )
            response.raise_for_status()
            payload = response.json()
            postings = payload.get("jobPostings", [])
            for posting in postings:
                job_id = (posting.get("bulletFields") or [None])[0]
                path = posting.get("externalPath")
                if not job_id or not path:
                    continue
                location = posting.get("locationsText")
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": posting.get("title", ""),
                        "locations": [location] if location else [],
                        "url": detail_base + path,
                    }
                )
            offset += len(postings)
            if not postings or len(postings) < page_size or offset >= payload.get("total", 0):
                break
    return jobs


def amazon_jobs() -> list[dict]:
    """Read Amazon's official JSON search feed, restricted to internships."""
    jobs = []
    offset = 0
    page_size = 100
    while True:
        payload = http.get_json(
            "https://www.amazon.jobs/en/search.json",
            params={
                "base_query": "intern",
                "offset": offset,
                "result_limit": page_size,
            },
        )
        page = payload.get("jobs", [])
        for job in page:
            locations = job.get("locations")
            if isinstance(locations, str):
                locations = [locations]
            elif not isinstance(locations, list):
                locations = []
            if not locations:
                city = ", ".join(
                    value for value in (job.get("city"), job.get("state")) if value
                )
                if city:
                    locations = [city]
            path = job.get("job_path") or job.get("job_url")
            url = path if isinstance(path, str) and path.startswith("http") else (
                "https://www.amazon.jobs" + path if path else None
            )
            if job.get("id") and job.get("title") and url:
                jobs.append(
                    {
                        "id": str(job["id"]),
                        "title": job["title"],
                        "locations": locations,
                        "url": url,
                    }
                )
        offset += len(page)
        if not page or len(page) < page_size:
            break
    return jobs


def databricks_jobs() -> list[dict]:
    """Read Databricks' official job-detail sitemap.

    The careers page renders the same detail URLs client-side. The official
    sitemap is a smaller, stable feed of those pages and avoids depending on
    the ATS that powers the site's backend.
    """
    sitemap_url = "https://www.databricks.com/careers-assets/sitemap/sitemap-0.xml"
    with http.session() as session:
        response = session.get(sitemap_url)
        response.raise_for_status()
        urls = re.findall(
            r"<loc>(https://www\.databricks\.com/company/careers/[^<]+)</loc>",
            response.text,
        )
    jobs = []
    seen = set()
    for url in urls:
        path = url.rstrip("/").rsplit("/", 1)[-1]
        match = re.search(r"-(\d{10})$", path)
        if not match or match.group(1) in seen:
            continue
        seen.add(match.group(1))
        title_slug = path[: match.start()]
        title = re.sub(r"-+", " ", unquote(title_slug)).strip().title()
        jobs.append(
            {
                "id": match.group(1),
                "title": title,
                "locations": [],
                "url": url,
            }
        )
    return jobs


def anthropic_jobs() -> list[dict]:
    """Read the listings rendered on Anthropic's official jobs page."""
    careers_url = "https://www.anthropic.com/careers/jobs"
    with http.session() as session:
        response = session.get(careers_url)
        response.raise_for_status()
        text = response.text
    jobs = []
    pattern = re.compile(
        r'<a href="(https://[^"/]+/anthropic/jobs/(\d+))"[^>]*>'
        r'(.*?)</a>',
        re.S,
    )
    for match in pattern.finditer(text):
        card = match.group(3)
        role = re.search(r"jobRole[^>]*>.*?<p[^>]*>(.*?)</p>", card, re.S)
        location = re.search(r"jobLocation[^>]*>.*?<p[^>]*>(.*?)</p>", card, re.S)
        if not role:
            continue
        clean = lambda value: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()
        jobs.append(
            {
                "id": match.group(2),
                "title": clean(role.group(1)),
                "locations": [clean(location.group(1))] if location else [],
                "url": match.group(1),
            }
        )
    return jobs


def ibm_jobs() -> list[dict]:
    """Read the internship search feed used by IBM Careers."""
    endpoint = "https://www-api.ibm.com/search/api/v1/ibmcom/appid/careers/agg"
    jobs = []
    seen = set()
    page = 1
    with http.session() as session:
        while True:
            response = session.get(
                endpoint,
                params={
                    "scope": "careers2",
                    "rmdt": "ALL",
                    "appid": "careers",
                    "sortby": "pageviews_desc",
                    "query": "intern",
                    "lang": "en",
                    "cc": "us",
                    "fr": 0,
                    "nr": 30,
                    "page": page,
                    "filter": "field_keyword_18:Internship",
                },
            )
            response.raise_for_status()
            search = response.json().get("resultset", {}).get("searchresults", {})
            results = search.get("searchresultlist", [])
            for result in results:
                url = result.get("url")
                if not isinstance(url, str) or "careers.ibm.com/" not in url:
                    continue
                attributes = {
                    key: value
                    for attribute in result.get("docattributes", [])
                    for key, value in attribute.items()
                }
                job_id = attributes.get("field_text_01")
                if not job_id:
                    match = re.search(r"[?&]jobId=([^&]+)", url)
                    job_id = match.group(1) if match else result.get("id")
                if not job_id or str(job_id) in seen:
                    continue
                seen.add(str(job_id))
                location = attributes.get("field_keyword_19")
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": result.get("title", ""),
                        "locations": [location] if location else [],
                        "url": url,
                    }
                )

            total = int(search.get("totalresults") or 0)
            returned = int(search.get("numresults") or len(results))
            if not results or page >= (total + max(returned, 1) - 1) // max(returned, 1):
                break
            page += 1
    return jobs


def palantir_jobs() -> list[dict]:
    """Read Palantir's own careers-page postings API."""
    endpoint = "https://www.palantir.com/api/lever/v1/postings?state=published"
    jobs = []
    seen = set()
    cursor = None
    with http.session() as session:
        while True:
            url = endpoint if cursor is None else f"{endpoint}&offset={cursor}"
            response = session.get(url)
            response.raise_for_status()
            payload = response.json()
            for posting in payload.get("data", []):
                job_id = posting.get("id")
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)
                categories = posting.get("categories") or {}
                location = categories.get("location")
                locations = categories.get("allLocations") or (
                    [location] if location else []
                )
                urls = posting.get("urls") or {}
                url = urls.get("show") or "https://www.palantir.com/careers/open-positions/"
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": posting.get("text", ""),
                        "locations": locations,
                        "url": url,
                    }
                )
            if not payload.get("hasNext") or not payload.get("next"):
                break
            cursor = payload["next"]
    return jobs


def google_jobs() -> list[dict]:
    """Read the result records embedded in Google Careers' official search page."""
    url = "https://www.google.com/about/careers/applications/jobs/results/?q=intern"
    with http.session() as session:
        response = session.get(url)
        response.raise_for_status()
        text = response.text
    marker = "AF_initDataCallback({key: 'ds:1'"
    start = text.find(marker)
    if start < 0:
        raise ValueError("Google Careers result data was not present")
    data_start = text.find("data:", start) + len("data:")
    data_end = text.find(", sideChannel:", data_start)
    if data_start < len("data:") or data_end < 0:
        raise ValueError("Google Careers result data was malformed")
    rows = json.loads(text[data_start:data_end])[0]
    detail_links = {
        title: "https://www.google.com/about/careers/applications/" + path
        for path, title in re.findall(
            r'href="(jobs/results/[^" ]+)"[^>]*aria-label="Learn more about ([^"]+)"',
            text,
        )
    }
    jobs = []
    for row in rows:
        if len(row) < 10 or not row[0] or not row[1]:
            continue
        locations = [location[0] for location in (row[9] or []) if location]
        jobs.append(
            {
                "id": str(row[0]),
                "title": row[1],
                "locations": locations,
                "url": detail_links.get(row[1], row[2]),
            }
        )
    return jobs


def google_technical_internships(jobs: list[dict]) -> list[dict]:
    """Google's Student Researcher postings are internship-style technical roles."""
    return [
        job
        for job in jobs
        if "student researcher" in job["title"].lower()
        or technical_internships([job])
    ]


def phenom_jobs(careers_url: str) -> list[dict]:
    """Read the SSR JSON embedded in a Phenom-powered official careers page."""
    jobs = []
    seen = set()
    # Phenom defaults to ten results and relevance ordering can move jobs
    # between pages between two polls. Request a larger page so normal-sized
    # internship searches arrive in one deterministic response.
    page_size = 100
    with http.session() as session:
        first_page = None
        total_hits = None
        for offset in range(0, 1000, page_size):
            separator = "&" if "?" in careers_url else "?"
            # `size` is the Phenom page size. The similarly named `s`
            # parameter resets the keyword search on these boards, so leave
            # it out.
            url = f"{careers_url}{separator}from={offset}&size={page_size}"
            response = session.get(url)
            response.raise_for_status()
            match = re.search(r"phApp\.ddo\s*=\s*(\{.*?\});", response.text, re.S)
            if not match:
                raise ValueError(f"could not find embedded job data in {url}")
            data = json.loads(html.unescape(match.group(1)))
            search_data = data.get("eagerLoadRefineSearch", {}).get("data", {})
            page = search_data.get("jobs", [])
            if first_page is None:
                first_page = page
                # Phenom's aggregations repeat the total for the primary
                # facets. Pick the smallest facet total to avoid counting
                # multi-valued locations as separate jobs.
                totals = [
                    sum((agg.get("value") or {}).values())
                    for agg in (search_data.get("aggregations") or [])
                    if isinstance(agg.get("value"), dict)
                ]
                if totals:
                    total_hits = min(totals)
            for job in page:
                job_id = job.get("reqId") or job.get("jobId") or job.get("jobSeqNo")
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)
                locations = job.get("multi_location") or job.get("location") or []
                if isinstance(locations, str):
                    locations = [locations]
                jobs.append(
                    {
                        "id": str(job_id),
                        "title": job.get("title", ""),
                        "locations": locations,
                        "url": job.get("applyUrl") or careers_url,
                    }
                )
            if not page or len(page) < page_size or (
                total_hits is not None and len(jobs) >= total_hits
            ):
                break
    return jobs


def ashby_jobs(board: str) -> list[dict]:
    payload = http.get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    jobs = []
    for job in payload.get("jobs", []):
        location = job.get("location")
        locations = [location] if isinstance(location, str) and location else []
        jobs.append(
            {
                "id": str(job["id"]),
                "title": job["title"],
                "locations": locations,
                "url": job.get("jobUrl") or job.get("applyUrl"),
            }
        )
    return jobs


def technical_internships(jobs: list[dict]) -> list[dict]:
    """Keep internship/co-op postings in software, ML, AI, or research."""
    import re

    technical = (
        "software", "engineering", "machine learning", "artificial intelligence",
        "research", "data science", "data engineer", "developer", "robotics",
    )
    internship = re.compile(r"\b(intern|internship|co-op|coop)\b", re.IGNORECASE)
    return [
        job
        for job in jobs
        if internship.search(job["title"])
        and (
            any(term in job["title"].lower() for term in technical)
            or re.search(r"\bai\b|\bml\b", job["title"], re.IGNORECASE)
        )
    ]
