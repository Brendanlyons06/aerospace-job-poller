"""Deterministic coverage for the polling and adapter contracts.

Live career boards change independently from this repository, so network
checks live in :mod:`test_live_polling` and are deliberately opt-in.  These
tests use representative vendor payloads to keep the normal suite fast and
repeatable while still covering pagination, normalization, filtering, and the
poller's failure isolation.
"""

from __future__ import annotations

import importlib
import json
import re
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


# The deployed package is named ``careers``.  This checkout is named
# ``Job-poller``, so import it through importlib and put its parent on sys.path
# instead of requiring a particular checkout directory name.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PARENT = PROJECT_ROOT.parent
# ``unittest discover -s tests`` puts the checkout itself first on sys.path.
# The checkout contains ``http.py``, which would shadow the standard-library
# ``http`` package while requests imports urllib3.  Production invokes this
# package from its parent, and the test suite recreates that import layout.
sys.path[:] = [
    entry for entry in sys.path
    if Path(entry or ".").resolve() != PROJECT_ROOT
]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

PACKAGE = PROJECT_ROOT.name
ats = importlib.import_module(f"{PACKAGE}.ats")
check = importlib.import_module(f"{PACKAGE}.check")
companies_module = importlib.import_module(f"{PACKAGE}.companies")
db = importlib.import_module(f"{PACKAGE}.db")
feeds = importlib.import_module(f"{PACKAGE}.companies.feeds")
filters = importlib.import_module(f"{PACKAGE}.filters")
job_metadata = importlib.import_module(f"{PACKAGE}.job_metadata")
imc = importlib.import_module(f"{PACKAGE}.companies.imc")
meta_client = importlib.import_module(f"{PACKAGE}.companies.metacareers.client")
notify = importlib.import_module(f"{PACKAGE}.notify")
profiles = importlib.import_module(f"{PACKAGE}.profiles")
rippling = importlib.import_module(f"{PACKAGE}.companies.rippling")
rippling_client = importlib.import_module(f"{PACKAGE}.companies.rippling.client")
watch = importlib.import_module(f"{PACKAGE}.watch")


def job(job_id: str, title: str = "Software Engineering Intern") -> dict:
    return {
        "id": job_id,
        "title": title,
        "locations": ["Austin, TX"],
        "url": f"https://careers.example/jobs/{job_id}",
    }


class FakeResponse:
    def __init__(self, *, payload=None, text: str = "") -> None:
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, *, get_responses=(), post_responses=()) -> None:
        self.get_responses = iter(get_responses)
        self.post_responses = iter(post_responses)
        self.get_calls = []
        self.post_calls = []

    def __enter__(self):
        return self

    def __exit__(self, *exc_info) -> None:
        return None

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return next(self.get_responses)

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return next(self.post_responses)


class FeedNormalizationTests(unittest.TestCase):
    def test_imc_rejects_foreign_greenhouse_results(self) -> None:
        payload = {
            "jobs": [
                {
                    "id": 1,
                    "title": "Machine Learning Research Intern - Amsterdam",
                    "location": {"name": "Amsterdam, Netherlands"},
                    "absolute_url": "https://job/1",
                },
                {
                    "id": 2,
                    "title": "Machine Learning Research Intern - Chicago",
                    "location": {"name": "Chicago, United States"},
                    "absolute_url": "https://job/2",
                },
            ]
        }
        with patch.object(feeds.http, "get_json", return_value=payload):
            self.assertEqual([job["id"] for job in imc.fetch_jobs()], ["2"])

    def test_rippling_reads_live_search_config_and_paginates(self) -> None:
        next_data = {
            "props": {
                "pageProps": {"data": {"algoliaIndexName": "careers_index"}}
            }
        }
        careers_page = (
            '<script id="__NEXT_DATA__" type="application/json">'
            f"{json.dumps(next_data)}"
            "</script>"
            '<script src="/_next/static/chunks/pages/_app-build.js"></script>'
        )
        app_script = (
            'x.env.ALGOLIA_ENV;let u="APPID";'
            'x.env.ALGOLIA_ADMIN_API_KEY;let s="public-key"'
        )
        session = FakeSession(
            get_responses=[
                FakeResponse(text=careers_page),
                FakeResponse(text=app_script),
            ],
            post_responses=[
                FakeResponse(payload={"results": [{"hits": [{"jobId": "a"}], "nbPages": 2}]}),
                FakeResponse(payload={"results": [{"hits": [{"jobId": "b"}], "nbPages": 2}]}),
            ],
        )
        with patch.object(rippling_client.http, "session", return_value=session):
            self.assertEqual(
                rippling_client.fetch_job_hits(),
                [{"jobId": "a"}, {"jobId": "b"}],
            )

        self.assertEqual(len(session.post_calls), 2)
        first_url, first_kwargs = session.post_calls[0]
        self.assertEqual(
            first_url,
            "https://APPID-dsn.algolia.net/1/indexes/*/queries",
        )
        self.assertEqual(first_kwargs["headers"]["X-Algolia-API-Key"], "public-key")
        self.assertIn("page=0", first_kwargs["json"]["requests"][0]["params"])
        self.assertIn(
            "page=1",
            session.post_calls[1][1]["json"]["requests"][0]["params"],
        )

    def test_rippling_merges_us_locations_by_stable_job_id(self) -> None:
        def hit(job_id, title, location, country="US"):
            return {
                "jobId": job_id,
                "name": title,
                "locations": [{"name": location, "countryCode": country}],
                "url": f"https://ats.rippling.com/rippling/jobs/{job_id}",
            }

        payload = [
            hit("swe", "Software Engineer Intern", "Seattle, WA"),
            hit("swe", "Software Engineer Intern", "San Francisco, CA"),
            hit("foreign", "Machine Learning Intern", "Toronto, Canada", "CA"),
            hit("sales", "Sales Intern", "New York, NY"),
            hit("false-match", "International Program Manager", "New York, NY"),
        ]
        with patch.object(rippling.client, "fetch_job_hits", return_value=payload):
            self.assertEqual(
                rippling.fetch_jobs(),
                [
                    {
                        "id": "swe",
                        "title": "Software Engineer Intern",
                        "locations": ["Seattle, WA", "San Francisco, CA"],
                        "url": "https://ats.rippling.com/rippling/jobs/swe",
                    }
                ],
            )

    def test_greenhouse_normalizes_metadata_and_deduplicates_locations(self) -> None:
        payload = {
            "jobs": [
                {
                    "id": 7,
                    "title": "Research Intern",
                    "absolute_url": "https://board/jobs/7",
                    "location": {"name": "New York, NY"},
                    "metadata": [
                        {"name": "Location", "value": ["New York, NY", "Remote"]}
                    ],
                }
            ]
        }
        with patch.object(feeds.http, "get_json", return_value=payload):
            self.assertEqual(
                feeds.greenhouse_jobs("example"),
                [
                    {
                        "id": "7",
                        "title": "Research Intern",
                        "locations": ["New York, NY", "Remote"],
                        "url": "https://board/jobs/7",
                    }
                ],
            )

    def test_ashby_normalizes_missing_location_and_fallback_url(self) -> None:
        payload = {
            "jobs": [
                {"id": "a", "title": "ML Intern", "location": None, "applyUrl": "https://apply/a"},
                {"id": "b", "title": "Research Intern", "location": "Remote", "jobUrl": "https://job/b"},
            ]
        }
        with patch.object(feeds.http, "get_json", return_value=payload):
            jobs = feeds.ashby_jobs("example")
        self.assertEqual([item["locations"] for item in jobs], [[], ["Remote"]])
        self.assertEqual([item["url"] for item in jobs], ["https://apply/a", "https://job/b"])

    def test_ashby_uses_exact_employment_type_and_structured_country(self) -> None:
        us_address = {"postalAddress": {"addressCountry": "United States"}}
        payload = {
            "jobs": [
                {
                    "id": "us",
                    "title": "Machine Learning Intern",
                    "employmentType": "Intern",
                    "location": "Toronto",
                    "address": {"postalAddress": {"addressCountry": "Canada"}},
                    "secondaryLocations": [{"location": "New York", "address": us_address}],
                    "jobUrl": "https://job/us",
                },
                {
                    "id": "design",
                    "title": "Design Intern",
                    "employmentType": "Intern",
                    "location": "Austin",
                    "address": us_address,
                    "secondaryLocations": [],
                    "jobUrl": "https://job/design",
                },
                {
                    "id": "full",
                    "title": "Internal Tools Engineer",
                    "employmentType": "FullTime",
                    "location": "Austin",
                    "address": us_address,
                    "secondaryLocations": [],
                    "jobUrl": "https://job/full",
                },
            ]
        }
        with patch.object(feeds.http, "get_json", return_value=payload):
            self.assertEqual(
                feeds.ashby_internships_us("example"),
                [
                    {
                        "id": "us",
                        "title": "Machine Learning Intern",
                        "locations": ["New York"],
                        "url": "https://job/us",
                        "employment_type": "Intern",
                    }
                ],
            )

    def test_greenhouse_submits_custom_job_type_and_us_office_filters(self) -> None:
        base_page = '<script>{"customFields":[{"id":12,"options":[{"id":34,"name":"Internships"}]}]}</script>'
        result_page = '<script>{"jobPosts":{"data":[{"id":7,"title":"Software Engineering Summer Scholar","location":"Remote","absolute_url":"https://job/7"},{"id":8,"title":"Product Summer Scholar","location":"Remote","absolute_url":"https://job/8"}],"total_pages":1}}</script>'
        session = FakeSession(
            get_responses=[FakeResponse(text=base_page), FakeResponse(text=result_page)]
        )
        offices = {
            "offices": [
                {"id": 56, "name": "Austin", "location": "Austin, Texas, United States", "parent_id": None}
            ]
        }
        with (
            patch.object(feeds.http, "session", return_value=session),
            patch.object(feeds.http, "get_json", return_value=offices),
        ):
            jobs = feeds.greenhouse_internships_us("example")
        self.assertEqual([item["id"] for item in jobs], ["7"])
        self.assertEqual(jobs[0]["locations"], ["Remote, United States"])
        params = session.get_calls[1][1]["params"]
        self.assertIn(("field_12[]", 34), params)
        self.assertIn(("offices[]", 56), params)

    def test_amazon_paginates_and_normalizes_relative_urls(self) -> None:
        first = {
            "jobs": [
                {"id": str(index), "title": "Software Intern", "locations": "Seattle, WA", "job_path": f"/en/jobs/{index}"}
                for index in range(100)
            ]
        }
        second = {"jobs": [{"id": "100", "title": "Software Intern", "locations": "Seattle, WA", "job_path": "/en/jobs/100"}]}
        with patch.object(feeds.http, "get_json", side_effect=[first, second]) as get_json:
            jobs = feeds.amazon_jobs()
        self.assertEqual(jobs[0], job("0", "Software Intern") | {"locations": ["Seattle, WA"], "url": "https://www.amazon.jobs/en/jobs/0"})
        self.assertEqual(jobs[-1], job("100", "Software Intern") | {"locations": ["Seattle, WA"], "url": "https://www.amazon.jobs/en/jobs/100"})
        self.assertEqual(get_json.call_count, 2)
        self.assertEqual(get_json.call_args_list[0].kwargs["params"]["offset"], 0)
        self.assertEqual(get_json.call_args_list[1].kwargs["params"]["offset"], 100)

    def test_workday_paginates_with_search_and_facets(self) -> None:
        session = FakeSession(
            post_responses=[
                FakeResponse(payload={"total": 21, "jobPostings": [
                    {"bulletFields": [str(index)], "externalPath": f"/job/{index}", "title": "AI Intern", "locationsText": "Austin, TX"}
                    for index in range(20)
                ]}),
                FakeResponse(payload={"total": 21, "jobPostings": [
                    {"bulletFields": ["20"], "externalPath": "/job/20", "title": "AI Intern", "locationsText": "Austin, TX"}
                ]}),
            ]
        )
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.workday_jobs("tenant", "External", search_text="intern", applied_facets={"type": ["intern"]})
        self.assertEqual(len(jobs), 21)
        self.assertEqual(jobs[0], job("0", "AI Intern") | {"url": "https://tenant.wd5.myworkdayjobs.com/en-US/External/job/0"})
        self.assertEqual(session.post_calls[0][1]["json"]["appliedFacets"], {"type": ["intern"]})
        self.assertEqual(session.post_calls[0][1]["json"]["searchText"], "intern")
        self.assertEqual(session.post_calls[1][1]["json"]["offset"], 20)

    def test_workday_discovers_live_type_and_country_facet_ids(self) -> None:
        discovery = FakeSession(post_responses=[FakeResponse(payload={"facets": [
            {"facetParameter": "workerSubType", "descriptor": "Job Type", "values": [
                {"descriptor": "Regular", "id": "regular"},
                {"descriptor": "Intern (Fixed Term)", "id": "intern"},
            ]},
            {"facetParameter": "locationMainGroup", "values": [
                {"facetParameter": "locationHierarchy1", "descriptor": "Locations", "values": [
                    {"descriptor": "Canada", "id": "ca"},
                    {"descriptor": "United States", "id": "us"},
                ]}
            ]},
        ]})])
        results = FakeSession(post_responses=[FakeResponse(payload={
            "total": 2,
            "jobPostings": [
                {
                    "bulletFields": ["R1"],
                    "externalPath": "/job/R1",
                    "title": "ML Engineering Intern",
                    "locationsText": "US, NY, New York",
                },
                {
                    "bulletFields": ["R2"],
                    "externalPath": "/job/R2",
                    "title": "Product Intern",
                    "locationsText": "US, NY, New York",
                },
            ],
        })])
        with patch.object(feeds.http, "session", side_effect=[discovery, results]):
            jobs = feeds.workday_internships_us("tenant", "External")
        self.assertEqual([item["id"] for item in jobs], ["R1"])
        self.assertEqual(
            results.post_calls[0][1]["json"]["appliedFacets"],
            {"workerSubType": ["intern"], "locationHierarchy1": ["us"]},
        )

    def test_official_page_extraction_uses_stable_id_once(self) -> None:
        session = FakeSession(get_responses=[FakeResponse(text="""
            <a href=\"/jobs/123\"> <span>Software Intern</span> </a>
            <a href=\"/jobs/123\">duplicate</a>
            <a href=\"/jobs/999\"></a>
        """)])
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.official_page_jobs("https://careers.example/openings", r"/jobs/(\d+)")
        self.assertEqual(jobs, [job("123", "Software Intern") | {"locations": [], "url": "https://careers.example/jobs/123"}])

    def test_pinpoint_uses_structured_us_location_and_source_metadata(self) -> None:
        payload = {
            "data": [
                {
                    "id": 501840,
                    "title": "LTVS Systems Engineering Intern",
                    "location": {"name": "Hawthorne, California"},
                    "url": "https://example.pinpointhq.com/postings/abc",
                    "deadline_at": "2026-10-01T00:00:00Z",
                    "employment_type_text": "Internship",
                    "workplace_type": "onsite",
                },
                {
                    "id": 2,
                    "title": "Systems Engineering Intern",
                    "location": {"name": "Toronto, Ontario"},
                    "url": "https://example.pinpointhq.com/postings/foreign",
                },
                {
                    "id": 3,
                    "title": "Product Design Intern",
                    "location": {"name": "Austin, Texas"},
                    "url": "https://example.pinpointhq.com/postings/irrelevant",
                },
            ]
        }
        with patch.object(feeds.http, "get_json", return_value=payload):
            jobs = feeds.pinpoint_internships_us(
                "example.pinpointhq.com",
                title_filter=filters.is_aerospace_mechanical_title,
            )
        self.assertEqual(
            jobs,
            [
                {
                    "id": "501840",
                    "title": "LTVS Systems Engineering Intern",
                    "locations": ["Hawthorne, California"],
                    "url": "https://example.pinpointhq.com/postings/abc",
                    "closes_at": "2026-10-01T00:00:00Z",
                    "employment_type": "Internship",
                    "work_mode": "onsite",
                }
            ],
        )

    def test_clearcompany_paginates_and_uses_structured_us_locations(self) -> None:
        first = {
            "results": [
                {
                    "id": "mechanical",
                    "positionTitle": "Mechanical Engineering Intern",
                    "locations": [
                        {"city": "Cedar Park", "subdivision": "TX", "country": "US"}
                    ],
                    "applyLink": "https://job/mechanical",
                },
                {
                    "id": "foreign",
                    "positionTitle": "Propulsion Engineering Intern",
                    "locations": [
                        {"city": "Toronto", "subdivision": "ON", "country": "CA"}
                    ],
                    "applyLink": "https://job/foreign",
                },
            ],
            "totalCount": 101,
        }
        second = {
            "results": [
                {
                    "id": "quality",
                    "positionTitle": "Quality Engineering Intern",
                    "locations": [
                        {"city": "Austin", "subdivision": "TX", "country": "US"}
                    ],
                    "applyLink": "https://job/quality",
                }
            ],
            "totalCount": 101,
        }
        session = FakeSession(
            get_responses=[FakeResponse(payload=first), FakeResponse(payload=second)]
        )
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.clearcompany_internships_us(
                "site", title_filter=filters.is_aerospace_mechanical_title
            )
        self.assertEqual([item["id"] for item in jobs], ["mechanical", "quality"])
        self.assertEqual(jobs[0]["locations"], ["Cedar Park, TX"])
        self.assertEqual(session.get_calls[1][1]["params"]["pageIndex"], 1)

    def test_impulse_reads_embedded_pinpoint_jobs(self) -> None:
        postings = {
            "props": {
                "pageProps": {
                    "jobPostings": {
                        "data": [
                            {
                                "title": "Thermal Engineering Intern",
                                "url": "https://impulsespace.pinpointhq.com/en/postings/abc-123",
                                "location": {
                                    "name": "Redondo Beach",
                                    "province": "California",
                                },
                            },
                            {
                                "title": "Mechanical Engineering Intern",
                                "url": "https://impulsespace.pinpointhq.com/en/postings/foreign-1",
                                "location": {"name": "Toronto", "province": "Ontario"},
                            },
                        ]
                    }
                }
            }
        }
        page = (
            '<script id="__NEXT_DATA__" type="application/json">'
            f"{json.dumps(postings)}"
            "</script>"
        )
        session = FakeSession(get_responses=[FakeResponse(text=page)])
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.impulse_space_internships_us(
                title_filter=filters.is_aerospace_mechanical_title
            )
        self.assertEqual([item["id"] for item in jobs], ["abc-123"])
        self.assertEqual(jobs[0]["locations"], ["Redondo Beach, California"])

    def test_icims_normalizes_us_location_and_filters_false_keyword_hits(self) -> None:
        def card(job_id: str, title: str, location: str) -> str:
            return f"""
                <li class="iCIMS_JobCardItem"><div>
                  <span class="sr-only field-label">Job Locations</span>
                  <span>{location}</span>
                  <a href="https://careers.example/jobs/{job_id}/role/job?in_iframe=1">
                    <h3>{title}</h3>
                  </a>
                </div></li>
            """

        page = "".join(
            [
                card("12", "Flight Test Intern", "US-CA-Marina"),
                card("13", "Software Engineering Intern", "US-CA-Marina"),
                card("14", "Mechanical Engineering Intern", "CA-ON-Toronto"),
            ]
        )
        session = FakeSession(get_responses=[FakeResponse(text=page)])
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.icims_internships_us(
                "careers.example",
                title_filter=filters.is_aerospace_mechanical_title,
            )
        self.assertEqual([item["id"] for item in jobs], ["12"])
        self.assertEqual(jobs[0]["locations"], ["Marina, CA, United States"])

    def test_eightfold_paginates_and_reflows_packed_locations(self) -> None:
        first = FakeResponse(payload={"count": 2, "positions": [
            {
                "id": 790315673635,
                "name": "Software Engineer Intern",
                "locations": ["Los Gatos,California,United States of America"],
                "canonicalPositionUrl": "https://host/careers/job/790315673635",
            }
        ]})
        second = FakeResponse(payload={"count": 2, "positions": [
            {"id": 42, "name": "ML Intern", "location": "Remote,United States"}
        ]})
        session = FakeSession(get_responses=[first, second])
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.eightfold_jobs("host", "example.com")
        self.assertEqual(
            jobs,
            [
                {
                    "id": "790315673635",
                    "title": "Software Engineer Intern",
                    "locations": ["Los Gatos, California, United States of America"],
                    "url": "https://host/careers/job/790315673635",
                },
                {
                    "id": "42",
                    "title": "ML Intern",
                    "locations": ["Remote, United States"],
                    "url": "https://host/careers/job/42",
                },
            ],
        )
        self.assertEqual(session.get_calls[0][1]["params"]["start"], 0)
        self.assertEqual(session.get_calls[1][1]["params"]["start"], 1)

    def test_phenom_uses_stable_req_ids_and_multilocations(self) -> None:
        page = {
            "eagerLoadRefineSearch": {
                "data": {
                    "jobs": [{"reqId": "R1", "title": "Engineering Intern", "multi_location": ["Austin, TX", "Remote"], "applyUrl": "https://apply/r1"}],
                    "aggregations": [{"value": {"intern": 1}}],
                }
            }
        }
        # The page embeds JSON, not Python repr; make the fixture match it.
        import json
        session = FakeSession(get_responses=[FakeResponse(text=f"<script>phApp.ddo = {json.dumps(page)};</script>")])
        with patch.object(feeds.http, "session", return_value=session):
            jobs = feeds.phenom_jobs("https://careers.example/search?keywords=intern")
        self.assertEqual(jobs, [job("R1", "Engineering Intern") | {"locations": ["Austin, TX", "Remote"], "url": "https://apply/r1"}])


class AtsTests(unittest.TestCase):
    def test_greenhouse_adapter_normalizes_nullable_location(self) -> None:
        with patch.object(ats.http, "get_json", return_value={"jobs": [{"id": 1, "title": "Intern", "location": None, "absolute_url": "https://job/1"}]}):
            self.assertEqual(ats.greenhouse("board"), [{"id": "1", "title": "Intern", "locations": [], "url": "https://job/1"}])

    def test_lever_adapter_uses_official_intern_commitment(self) -> None:
        postings = [
            {"id": "intern", "text": "Software Intern", "hostedUrl": "https://job/intern", "categories": {"commitment": "Intern", "allLocations": ["Remote"]}},
            {"id": "full", "text": "Software Engineer", "hostedUrl": "https://job/full", "categories": {"commitment": "Full-time", "location": "Austin, TX"}},
        ]
        with patch.object(ats.http, "get_json", return_value=postings):
            self.assertEqual(
                ats.lever("board", commitment="Intern"),
                [job("intern", "Software Intern") | {
                    "locations": ["Remote"],
                    "url": "https://job/intern",
                    "employment_type": "Intern",
                }],
            )

    def test_lever_can_restrict_exact_intern_commitment_to_us_locations(self) -> None:
        postings = [
            {"id": "us", "text": "Design Intern", "hostedUrl": "https://job/us", "categories": {"commitment": "Intern", "allLocations": ["Austin, TX"]}},
            {"id": "ca", "text": "Design Intern", "hostedUrl": "https://job/ca", "categories": {"commitment": "Intern", "allLocations": ["Toronto, Canada"]}},
        ]
        with patch.object(ats.http, "get_json", return_value=postings):
            self.assertEqual(
                [item["id"] for item in ats.lever("board", commitment="Intern", country="United States")],
                ["us"],
            )


class MetaClientTests(unittest.TestCase):
    def test_search_jobs_closes_its_session_and_sends_filters(self) -> None:
        session = Mock()
        response = Mock()
        response.json.return_value = {"data": {"jobs": []}}
        session.post.return_value = response
        with (
            patch.object(meta_client.http, "session", return_value=session),
            patch.object(meta_client, "get_lsd_token", return_value="token"),
        ):
            self.assertEqual(
                meta_client.search_jobs(roles=["Internship"], teams=["Software Engineering"]),
                {"data": {"jobs": []}},
            )
        request = session.post.call_args.kwargs
        self.assertEqual(request["headers"]["x-fb-lsd"], "token")
        self.assertEqual(
            json.loads(request["data"]["variables"])["search_input"]["roles"],
            ["Internship"],
        )
        session.close.assert_called_once()

    def test_search_jobs_closes_its_session_when_the_request_fails(self) -> None:
        session = Mock()
        session.post.side_effect = RuntimeError("temporary failure")
        with (
            patch.object(meta_client.http, "session", return_value=session),
            patch.object(meta_client, "get_lsd_token", return_value="token"),
            self.assertRaisesRegex(RuntimeError, "temporary failure"),
        ):
            meta_client.search_jobs()
        session.close.assert_called_once()


class AdapterContractTests(unittest.TestCase):
    def test_phase_three_workflow_enables_the_50_adapter_manifest(self) -> None:
        workflow = (PROJECT_ROOT / ".github/workflows/hourly-poller.yml").read_text()
        match = re.search(r"^\s*JOB_POLLER_COMPANIES:\s*(\S+)$", workflow, re.MULTILINE)
        self.assertIsNotNone(match)
        slugs = match.group(1).split(",")
        self.assertEqual(len(slugs), 50)
        self.assertEqual(len(set(slugs)), 50)
        enabled_names = {
            importlib.import_module(f"{PACKAGE}.companies.{slug}").COMPANY_NAME
            for slug in slugs
        }
        self.assertEqual(enabled_names, profiles.AEROSPACE_ADAPTER_COMPANIES)
        self.assertTrue(enabled_names.issubset(profiles.AEROSPACE_TARGET_COMPANIES))

    def test_every_discovered_adapter_declares_the_fetch_contract(self) -> None:
        self.assertGreaterEqual(len(companies_module.COMPANIES), 1)
        for company in companies_module.COMPANIES:
            with self.subTest(company=company.__name__):
                self.assertIsInstance(company.COMPANY_NAME, str)
                self.assertTrue(company.COMPANY_NAME.strip())
                self.assertTrue(callable(company.fetch_jobs))

    def test_every_filter_is_non_mutating_and_returns_a_subset(self) -> None:
        source = [
            job("intern", "Software Engineering Intern"),
            job("fulltime", "Software Engineer"),
            job("sales", "Sales Intern"),
            job("phd", "Machine Learning PhD Intern"),
        ]
        original = [item.copy() for item in source]
        for company in companies_module.COMPANIES:
            if not hasattr(company, "filter_jobs"):
                continue
            with self.subTest(company=company.__name__):
                filtered = company.filter_jobs(source)
                self.assertIsInstance(filtered, list)
                self.assertTrue({item["id"] for item in filtered}.issubset({item["id"] for item in source}))
                self.assertEqual(source, original)

    def test_technical_internship_filter_excludes_non_technical_and_non_intern_roles(self) -> None:
        self.assertEqual(
            feeds.technical_internships([
                job("a", "Software Engineering Intern"),
                job("b", "Sales Intern"),
                job("c", "Software Engineer"),
                job("d", "Machine Learning Co-op"),
                job("e", "Hardware Engineering Intern"),
                job("f", "Data Science Intern"),
                job("g", "Research Intern"),
            ]),
            [job("a", "Software Engineering Intern"), job("d", "Machine Learning Co-op")],
        )

    def test_swe_ml_title_classifier_covers_real_title_variants(self) -> None:
        accepted = [
            "Software Engineering Intern",
            "Software Engineer Co-op",
            "Software Development Engineer Internship",
            "Software Developer Intern",
            "Software Intern",
            "SWE Intern",
            "SDE Co-op",
            "Machine-Learning Intern",
            "ML Engineering Intern",
            "AI/ML Research Intern",
            "Artificial Intelligence Internship",
            "AI Engineer Co-op",
            "Student Researcher, Machine Learning",
            "Quantitative Developer Intern - Summer 2027",
            "Quant Dev Intern",
        ]
        rejected = [
            "Design Intern",
            "Finance Co-op",
            "Sales Intern",
            "Product Management Intern",
            "Quantitative Trader Intern",
            "Quantitative Researcher Intern",
            "Hardware Engineering Intern",
            "Mechanical Engineering Intern",
            "Data Science Intern",
            "Data Engineering Intern",
            "Research Intern",
            "Internal Tools Engineer",
        ]
        for title in accepted:
            with self.subTest(title=title):
                self.assertTrue(filters.is_swe_ml_title(title))
        for title in rejected:
            with self.subTest(title=title):
                self.assertFalse(filters.is_swe_ml_title(title))

    def test_internship_us_fallback_handles_board_location_formats(self) -> None:
        source = [
            job("state", "Software Engineering Intern") | {"locations": ["Austin, TX"]},
            job("country", "ML Co-op") | {"locations": ["Remote - United States"]},
            job("foreign", "SWE Intern") | {"locations": ["Toronto, Canada"]},
            job("design", "Design Intern") | {"locations": ["Austin, TX"]},
            job("internal", "Internal Tools Engineer") | {"locations": ["Austin, TX"]},
        ]
        self.assertEqual(
            [item["id"] for item in filters.internships_in_us(source)],
            ["state", "country"],
        )

    def test_aerospace_classifier_and_generic_company_exception(self) -> None:
        accepted = [
            "Mechanical Engineering Intern",
            "Systems Engineering Intern",
            "Flight Test Engineering Co-op",
            "GNC Intern",
            "Manufacturing Engineering Intern",
        ]
        for title in accepted:
            with self.subTest(title=title):
                self.assertTrue(filters.is_aerospace_mechanical_title(title))

        self.assertFalse(
            filters.is_aerospace_mechanical_title("Flight Software Engineering Intern")
        )
        self.assertTrue(
            filters.is_generic_engineering_internship_title(
                "Summer 2027 Engineering Internship/Co-op"
            )
        )
        self.assertFalse(
            filters.is_generic_engineering_internship_title(
                "Summer 2027 Civil Engineering Internship"
            )
        )

    def test_checker_rejects_duplicate_or_malformed_poll_results(self) -> None:
        errors = check._validate([
            job("same"),
            job("same"),
            {"id": "", "title": "Intern", "locations": [1], "url": "not-a-url"},
        ], "poll")
        self.assertTrue(any("duplicate" in error for error in errors))
        self.assertTrue(any("empty" in error for error in errors))
        self.assertTrue(any("list of str" in error for error in errors))
        self.assertTrue(any("not a URL" in error for error in errors))


class DashboardMetadataTests(unittest.TestCase):
    def test_company_sector_is_separate_from_job_discipline(self) -> None:
        self.assertEqual(
            job_metadata.company_sector("SpaceX"),
            "space-launch-spacecraft",
        )
        self.assertEqual(
            job_metadata.company_sector("Northrop Grumman"),
            "aerospace-defense",
        )
        self.assertEqual(
            job_metadata.classify_discipline("Mechanical Design Engineering Intern"),
            "mechanical-design",
        )

    def test_specific_discipline_rules_take_priority(self) -> None:
        cases = {
            "GNC Engineering Intern": "gnc",
            "Flight Controls Intern": "flight-controls",
            "Systems Integration & Test Intern": "systems-integration-test",
            "Propulsion Engineering Intern": "propulsion",
            "General Engineering Intern": "general-engineering",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(job_metadata.classify_discipline(title), expected)

    def test_broader_stem_disciplines_and_coops_are_classified(self) -> None:
        cases = {
            "Electrical Engineering Intern": "electrical",
            "Civil Engineering Co-op": "civil",
            "Machine Learning Internship": "data-science",
            "Embedded Software Engineering Intern": "software",
            "Materials Science Intern": "materials",
            "Supply Chain Operations Intern": "supply-chain",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(job_metadata.classify_discipline(title), expected)
        self.assertEqual(
            job_metadata.normalize_employment_type(None, "Civil Engineering Co-op"),
            "co-op",
        )

    def test_locations_are_structured_without_discarding_source_label(self) -> None:
        standard = job_metadata.structured_location("Long Beach, California, United States")
        reverse = job_metadata.structured_location("US, NY, New York")
        workday = job_metadata.structured_location("United States-Virginia-Dulles")
        remote = job_metadata.structured_location("Remote, United States")
        self.assertEqual(
            (standard["city"], standard["state"], standard["country"]),
            ("Long Beach", "CA", "US"),
        )
        self.assertEqual((reverse["city"], reverse["state"]), ("New York", "NY"))
        self.assertEqual((workday["city"], workday["state"]), ("Dulles", "VA"))
        self.assertIsNone(remote["city"])
        self.assertEqual(remote["label"], "Remote, United States")

    def test_ats_site_locations_are_normalized_to_city_and_state(self) -> None:
        cases = {
            "US-CA-EL SEGUNDO-R01 ~ 2000 E Imperial Hwy ~ BLDG R01": ("El Segundo", "CA"),
            "US-CO-AURORA-S75 ~ 16800 E Centretech Pkwy ~ BLDG S75": ("Aurora", "CO"),
            "US-NY-East Farmingdale (TR)": ("East Farmingdale", "NY"),
        }
        for label, expected in cases.items():
            with self.subTest(label=label):
                location = job_metadata.structured_location(label)
                self.assertEqual((location["city"], location["state"]), expected)
                self.assertEqual(location["label"], label)

    def test_optional_dashboard_fields_are_normalized(self) -> None:
        enriched = job_metadata.enrich_job(
            "Joby Aviation",
            job("42", "Hybrid Flight Test Engineering Intern") | {
                "posted_at": 1_787_500_800_000,
                "compensation": {
                    "min": "30.50",
                    "max": 42,
                    "currency": "USD",
                    "period": "hour",
                },
            },
        )
        self.assertEqual(enriched["work_mode"], "hybrid")
        self.assertEqual(enriched["discipline"], "flight-test")
        self.assertEqual(enriched["compensation_min"], 30.5)
        self.assertTrue(enriched["posted_at"].endswith("+00:00"))


class DatabaseDiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "jobs.db"
        self.db_path_patch = patch.object(db, "DB_PATH", self.db_path)
        self.db_path_patch.start()

    def tearDown(self) -> None:
        self.db_path_patch.stop()
        self.temp_dir.cleanup()

    def test_first_poll_seeds_database_and_later_poll_returns_only_new_job(self) -> None:
        existing = job("existing")
        newly_posted = job("new", "Machine Learning Intern")

        self.assertEqual(db.sync_and_get_new("Example", [existing]), [])
        self.assertEqual(db.sync_and_get_new("Example", [existing]), [])
        self.assertEqual(
            db.sync_and_get_new("Example", [existing, newly_posted]),
            [newly_posted],
        )
        # Until delivery is acknowledged, a later poll returns the durable
        # outbox item again instead of silently losing the alert.
        self.assertEqual(
            db.sync_and_get_new("Example", [existing, newly_posted]),
            [newly_posted],
        )
        db.mark_notification_delivered("Example", newly_posted["id"])
        self.assertEqual(db.sync_and_get_new("Example", [existing, newly_posted]), [])

        connection = db._connect()
        try:
            stored_ids = connection.execute(
                "SELECT job_id FROM jobs WHERE company = ? ORDER BY job_id",
                ("Example",),
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual(stored_ids, [("existing",), ("new",)])

    def test_failed_notification_stays_pending_with_attempt_metadata(self) -> None:
        existing = job("existing")
        newly_posted = job("new", "Mechanical Engineering Intern")
        db.sync_and_get_new("Example", [existing])
        self.assertEqual(db.sync_and_get_new("Example", [existing, newly_posted]), [newly_posted])

        db.mark_notification_failed("Example", "new", "SMTP temporarily unavailable")
        self.assertEqual(db.sync_and_get_new("Example", [existing]), [newly_posted])

        connection = db._connect()
        try:
            attempts, error, delivered_at = connection.execute(
                "SELECT attempts, last_error, delivered_at FROM notification_outbox "
                "WHERE company = ? AND job_id = ?",
                ("Example", "new"),
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(attempts, 1)
        self.assertEqual(error, "SMTP temporarily unavailable")
        self.assertIsNone(delivered_at)

    def test_health_alert_threshold_recovery_and_weekly_schedule(self) -> None:
        self.assertEqual(db.record_poll_failure("Example", "one"), (1, False))
        self.assertEqual(db.record_poll_failure("Example", "two"), (2, False))
        self.assertEqual(db.record_poll_failure("Example", "three"), (3, True))
        self.assertEqual(db.record_poll_failure("Example", "four"), (4, False))
        self.assertEqual(db.record_poll_success("Example", 0), (True, 1))
        self.assertEqual(db.record_poll_success("Example", 0), (False, 2))
        self.assertEqual(db.record_poll_success("Example", 5), (False, 0))

        started = datetime(2026, 8, 24, tzinfo=timezone.utc)
        self.assertFalse(db.weekly_summary_due(now=started))
        self.assertFalse(db.weekly_summary_due(now=started + timedelta(days=6)))
        self.assertTrue(db.weekly_summary_due(now=started + timedelta(days=7)))
        db.mark_weekly_summary_sent(now=started + timedelta(days=7))
        self.assertFalse(db.weekly_summary_due(now=started + timedelta(days=8)))

        completed = started + timedelta(hours=2)
        db.mark_poll_completed(now=completed)
        connection = db._connect()
        try:
            stored = connection.execute(
                "SELECT value FROM system_meta WHERE key = 'last_poll_completed_at'"
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(stored, completed.isoformat())

    def test_dashboard_rows_and_two_poll_closure_lifecycle(self) -> None:
        posting = job("phase-2", "Mechanical Design Engineering Intern") | {
            "locations": ["Long Beach, CA"],
            "posted_at": "2026-08-20T12:00:00Z",
            "closes_at": "2026-09-15T23:59:59Z",
            "work_mode": "hybrid",
            "compensation": {
                "min": 28,
                "max": 36,
                "currency": "USD",
                "period": "hour",
            },
            "location_details": [{
                "label": "Long Beach, CA",
                "latitude": 33.7701,
                "longitude": -118.1937,
            }],
        }
        db.sync_and_get_new(
            "SpaceX",
            [posting],
            company_slug="spacex",
            careers_url="https://www.spacex.com/careers/",
        )

        connection = db._connect()
        try:
            company_row = connection.execute(
                "SELECT slug, sector, careers_url FROM companies WHERE company = ?",
                ("SpaceX",),
            ).fetchone()
            job_row = connection.execute(
                "SELECT discipline, work_mode, posted_at, closes_at, last_seen, "
                "closed_at, compensation_min, compensation_max FROM jobs "
                "WHERE company = ? AND job_id = ?",
                ("SpaceX", "phase-2"),
            ).fetchone()
            location_row = connection.execute(
                "SELECT city, state, country, latitude, longitude FROM job_locations "
                "WHERE company = ? AND job_id = ?",
                ("SpaceX", "phase-2"),
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(
            company_row,
            ("spacex", "space-launch-spacecraft", "https://www.spacex.com/careers/"),
        )
        self.assertEqual(job_row[:4], (
            "mechanical-design", "hybrid", "2026-08-20T12:00:00+00:00",
            "2026-09-15T23:59:59+00:00",
        ))
        self.assertIsNotNone(job_row[4])
        self.assertIsNone(job_row[5])
        self.assertEqual(job_row[6:], (28.0, 36.0))
        self.assertEqual(location_row, ("Long Beach", "CA", "US", 33.7701, -118.1937))

        db.sync_and_get_new("SpaceX", [])
        connection = db._connect()
        try:
            self.assertIsNone(connection.execute(
                "SELECT closed_at FROM jobs WHERE company = ? AND job_id = ?",
                ("SpaceX", "phase-2"),
            ).fetchone()[0])
        finally:
            connection.close()

        db.sync_and_get_new("SpaceX", [])
        connection = db._connect()
        try:
            self.assertIsNotNone(connection.execute(
                "SELECT closed_at FROM jobs WHERE company = ? AND job_id = ?",
                ("SpaceX", "phase-2"),
            ).fetchone()[0])
        finally:
            connection.close()

    def test_existing_sqlite_database_is_upgraded_without_losing_jobs(self) -> None:
        connection = sqlite3.connect(self.db_path)
        connection.execute(
            "CREATE TABLE jobs (company TEXT NOT NULL, job_id TEXT NOT NULL, "
            "title TEXT NOT NULL, locations TEXT NOT NULL, first_seen TEXT NOT NULL, "
            "PRIMARY KEY (company, job_id))"
        )
        connection.execute(
            "INSERT INTO jobs VALUES (?, ?, ?, ?, ?)",
            ("Example", "old", "Mechanical Intern", "Austin, TX", "2026-08-01"),
        )
        connection.commit()
        connection.close()

        upgraded = db._connect()
        try:
            columns = {row[1] for row in upgraded.execute("PRAGMA table_info(jobs)")}
            preserved = upgraded.execute(
                "SELECT title, first_seen, last_seen FROM jobs WHERE job_id = 'old'"
            ).fetchone()
        finally:
            upgraded.close()
        self.assertTrue({"discipline", "last_seen", "closed_at", "work_mode"} <= columns)
        self.assertEqual(preserved, ("Mechanical Intern", "2026-08-01", "2026-08-01"))


class DatabaseConfigurationTests(unittest.TestCase):
    def test_local_mode_defaults_to_sqlite(self) -> None:
        with patch.dict(
            db.os.environ,
            {"JOB_POLLER_DATABASE_URL": "", "JOB_POLLER_REQUIRE_POSTGRES": "false"},
        ):
            self.assertEqual(db.backend_name(), "sqlite")
            self.assertEqual(db.validate_configuration(), "sqlite")

    def test_cloud_mode_refuses_to_fall_back_to_sqlite(self) -> None:
        with patch.dict(
            db.os.environ,
            {"JOB_POLLER_DATABASE_URL": "", "JOB_POLLER_REQUIRE_POSTGRES": "true"},
        ):
            with self.assertRaisesRegex(RuntimeError, "requires.*DATABASE_URL"):
                db.validate_configuration()

    def test_postgres_parameter_markers_are_translated(self) -> None:
        connection = Mock()
        db._execute(
            connection,
            "SELECT 1 FROM jobs WHERE company = ? AND job_id = ?",
            ("Example", "123"),
        )
        connection.execute.assert_called_once_with(
            "SELECT 1 FROM jobs WHERE company = %s AND job_id = %s",
            ("Example", "123"),
        )

    def test_supabase_pooler_requires_project_reference_in_username(self) -> None:
        invalid_url = (
            "postgresql://postgres:encoded-password@"
            "aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        )
        with self.assertRaisesRegex(RuntimeError, "postgres.<project-reference>"):
            db._validate_database_url_shape(invalid_url)

    def test_supabase_transaction_pooler_shape_is_accepted(self) -> None:
        valid_url = (
            "postgresql://postgres.projectref:encoded-password@"
            "aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        )
        db._validate_database_url_shape(valid_url)

    def test_postgres_migration_enables_row_level_security(self) -> None:
        migration = (
            PROJECT_ROOT / "supabase" / "migrations" / "001_poller_state.sql"
        ).read_text()
        self.assertIn("ALTER TABLE jobs ENABLE ROW LEVEL SECURITY", migration)
        self.assertIn(
            "ALTER TABLE notification_outbox ENABLE ROW LEVEL SECURITY", migration
        )
        dashboard_migration = (
            PROJECT_ROOT / "supabase" / "migrations" / "002_dashboard_ready_data.sql"
        ).read_text()
        self.assertIn("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS discipline", dashboard_migration)
        self.assertIn("CREATE TABLE IF NOT EXISTS job_locations", dashboard_migration)
        self.assertIn("ALTER TABLE job_locations ENABLE ROW LEVEL SECURITY", dashboard_migration)
        read_api_migration = (
            PROJECT_ROOT / "supabase" / "migrations" / "003_dashboard_read_api.sql"
        ).read_text()
        self.assertIn("CREATE VIEW public.dashboard_active_jobs", read_api_migration)
        self.assertIn("WHERE j.closed_at IS NULL", read_api_migration)
        self.assertIn("REVOKE ALL ON public.dashboard_active_jobs FROM PUBLIC", read_api_migration)
        self.assertIn("GRANT SELECT ON public.dashboard_active_jobs TO anon", read_api_migration)
        self.assertNotIn("notification_outbox", read_api_migration)
        status_migration = (
            PROJECT_ROOT / "supabase" / "migrations" / "004_dashboard_locations_and_status.sql"
        ).read_text()
        self.assertIn("AS location_items", status_migration)
        self.assertIn("CREATE VIEW public.dashboard_status", status_migration)
        self.assertIn("last_poll_completed_at", status_migration)
        self.assertIn("GRANT SELECT ON public.dashboard_status TO anon", status_migration)
        self.assertNotIn("notification_outbox", status_migration)
        health_migration = (
            PROJECT_ROOT / "supabase" / "migrations" / "005_dashboard_health_and_metrics.sql"
        ).read_text()
        self.assertIn("CREATE VIEW public.dashboard_sources", health_migration)
        self.assertIn("active_job_count", health_migration)
        self.assertIn("healthy_source_count", health_migration)
        self.assertIn("GRANT SELECT ON public.dashboard_sources TO anon", health_migration)
        self.assertNotIn("last_error", health_migration)
        self.assertNotIn("notification_outbox", health_migration)

    def test_cloud_workflow_requires_explicit_schedule_enablement(self) -> None:
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "hourly-poller.yml"
        ).read_text()
        self.assertIn("vars.POLLER_ENABLED == 'true'", workflow)
        self.assertIn("JOB_POLLER_REQUIRE_POSTGRES: \"true\"", workflow)
        self.assertIn("secrets.SUPABASE_DATABASE_URL", workflow)
        self.assertIn("default: test-notification", workflow)
        self.assertIn("actions/checkout@v6", workflow)
        self.assertIn("actions/setup-python@v6", workflow)

    def test_postgres_style_queries_preserve_dedup_and_outbox_behavior(self) -> None:
        class PostgresStyleConnection:
            """Exercise the PostgreSQL parameter path against an in-memory DB."""

            def __init__(self) -> None:
                self.inner = sqlite3.connect(":memory:")
                self.inner.executescript(db._SQLITE_SCHEMA)

            def execute(self, statement, parameters=()):
                return self.inner.execute(statement.replace("%s", "?"), parameters)

            def commit(self) -> None:
                self.inner.commit()

            def rollback(self) -> None:
                self.inner.rollback()

        connection = PostgresStyleConnection()
        existing = job("existing")
        newly_posted = job("new", "Mechanical Engineering Intern")
        with patch.object(db, "_connect", return_value=connection):
            self.assertEqual(db.sync_and_get_new("Example", [existing]), [])
            self.assertEqual(
                db.sync_and_get_new("Example", [existing, newly_posted]),
                [newly_posted],
            )
            db.mark_notification_delivered("Example", "new")
            self.assertEqual(
                db.sync_and_get_new("Example", [existing, newly_posted]), []
            )
        connection.inner.close()

class PollerTests(unittest.TestCase):
    def test_fetch_applies_company_filter(self) -> None:
        company = SimpleNamespace(
            COMPANY_NAME="Example",
            fetch_jobs=Mock(return_value=[job("1")]),
            filter_jobs=Mock(return_value=[job("1")]),
        )
        self.assertEqual(watch._fetch(company), [job("1")])
        company.filter_jobs.assert_called_once_with([job("1")])

    def test_run_keeps_polling_when_one_company_fails(self) -> None:
        class Company(SimpleNamespace):
            __hash__ = object.__hash__

        good = Company(COMPANY_NAME="Good", fetch_jobs=Mock(return_value=[job("good")]))
        bad = Company(COMPANY_NAME="Bad", fetch_jobs=Mock(side_effect=RuntimeError("board down")))
        with (
            patch.object(watch, "COMPANIES", [good, bad]),
            patch.object(watch.notify, "validate_configuration"),
            patch.object(watch.notify, "ensure_opted_in"),
            patch.object(watch.notify, "notify_new_job"),
            patch.object(watch.db, "record_poll_failure", return_value=(1, False)),
            patch.object(watch.db, "record_poll_success", return_value=(False, 0)),
            patch.object(watch.db, "weekly_summary_due", return_value=False),
            patch.object(watch.db, "mark_poll_completed"),
            patch.object(watch.db, "sync_and_get_new", return_value=[] ) as sync,
        ):
            watch.run()
        sync.assert_called_once_with("Good", [job("good")])

    def test_run_notifies_only_job_added_after_initial_poll(self) -> None:
        class Company(SimpleNamespace):
            __hash__ = object.__hash__

        existing = job("existing")
        newly_posted = job("new", "Machine Learning Intern")
        company = Company(
            COMPANY_NAME="Example",
            fetch_jobs=Mock(side_effect=[[existing], [existing, newly_posted]]),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch.object(db, "DB_PATH", Path(temp_dir) / "jobs.db"),
                patch.object(watch, "COMPANIES", [company]),
                patch.object(watch.notify, "validate_configuration"),
                patch.object(watch.notify, "ensure_opted_in"),
                patch.object(watch.notify, "notify_new_job") as notify_new_job,
                patch.object(watch.db, "mark_notification_delivered") as delivered,
                patch.object(watch.observability, "log_event"),
            ):
                watch.run()
                notify_new_job.assert_not_called()
                watch.run()

        notify_new_job.assert_called_once_with("Example", newly_posted)
        delivered.assert_called_once_with("Example", "new")


class EmailNotificationTests(unittest.TestCase):
    def test_email_only_configuration_does_not_require_twilio(self) -> None:
        with (
            patch.object(notify, "EMAIL_ALERTS_ENABLED", True),
            patch.object(notify, "SMS_ALERTS_ENABLED", False),
            patch.object(notify, "SMTP_USER", "sender@example.test"),
            patch.object(notify, "SMTP_PASSWORD", "app-password"),
            patch.object(notify, "EMAIL_TO", "one@example.test, two@example.test"),
        ):
            self.assertEqual(notify.validate_configuration(), ("email",))

    def test_configuration_requires_at_least_one_enabled_channel(self) -> None:
        with (
            patch.object(notify, "EMAIL_ALERTS_ENABLED", False),
            patch.object(notify, "SMS_ALERTS_ENABLED", False),
        ):
            with self.assertRaisesRegex(RuntimeError, "No alert channel is enabled"):
                notify.validate_configuration()

    def test_email_only_notification_never_calls_twilio(self) -> None:
        with (
            patch.object(notify, "validate_configuration", return_value=("email",)),
            patch.object(notify, "send_text") as send_text,
            patch.object(notify, "send_email") as send_email,
        ):
            delivered = notify.notify_new_job("Example", job("1"))

        self.assertEqual(delivered, ("email",))
        send_text.assert_not_called()
        send_email.assert_called_once()

    def test_sms_failure_does_not_prevent_email_delivery(self) -> None:
        with (
            patch.object(
                notify, "validate_configuration", return_value=("sms", "email")
            ),
            patch.object(notify, "send_text", side_effect=RuntimeError("Twilio down")),
            patch.object(notify, "send_email") as send_email,
            patch("builtins.print"),
        ):
            delivered = notify.notify_new_job("Example", job("1"))

        self.assertEqual(delivered, ("email",))
        send_email.assert_called_once()

    def test_send_email_authenticates_and_sends_expected_message(self) -> None:
        with (
            patch.object(notify, "SMTP_HOST", "smtp.example.test"),
            patch.object(notify, "SMTP_PORT", 2525),
            patch.object(notify, "SMTP_USER", "sender@example.test"),
            patch.object(notify, "SMTP_PASSWORD", "app-password"),
            patch.object(notify, "EMAIL_TO", "recipient@example.test"),
            patch.object(notify.smtplib, "SMTP") as smtp,
        ):
            notify.send_email("New Example posting", "A new role is available")

        smtp.assert_called_once_with("smtp.example.test", 2525)
        server = smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once_with()
        server.login.assert_called_once_with("sender@example.test", "app-password")
        server.send_message.assert_called_once()
        message = server.send_message.call_args.args[0]
        self.assertEqual(message["Subject"], "New Example posting")
        self.assertEqual(message["From"], "sender@example.test")
        self.assertEqual(message["To"], "recipient@example.test")
        self.assertEqual(message.get_payload(), "A new role is available")
