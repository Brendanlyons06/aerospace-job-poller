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
import sys
import tempfile
import unittest
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

PACKAGE = "Job-poller"
ats = importlib.import_module(f"{PACKAGE}.ats")
check = importlib.import_module(f"{PACKAGE}.check")
companies_module = importlib.import_module(f"{PACKAGE}.companies")
db = importlib.import_module(f"{PACKAGE}.db")
feeds = importlib.import_module(f"{PACKAGE}.companies.feeds")
filters = importlib.import_module(f"{PACKAGE}.filters")
meta_client = importlib.import_module(f"{PACKAGE}.companies.metacareers.client")
notify = importlib.import_module(f"{PACKAGE}.notify")
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
                    "title": "Design Intern",
                    "employmentType": "Intern",
                    "location": "Toronto",
                    "address": {"postalAddress": {"addressCountry": "Canada"}},
                    "secondaryLocations": [{"location": "New York", "address": us_address}],
                    "jobUrl": "https://job/us",
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
                        "title": "Design Intern",
                        "locations": ["New York"],
                        "url": "https://job/us",
                    }
                ],
            )

    def test_greenhouse_submits_custom_job_type_and_us_office_filters(self) -> None:
        base_page = '<script>{"customFields":[{"id":12,"options":[{"id":34,"name":"Internships"}]}]}</script>'
        result_page = '<script>{"jobPosts":{"data":[{"id":7,"title":"Summer Scholar","location":"Remote","absolute_url":"https://job/7"}],"total_pages":1}}</script>'
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
            "total": 1,
            "jobPostings": [{
                "bulletFields": ["R1"],
                "externalPath": "/job/R1",
                "title": "Product Intern",
                "locationsText": "US, NY, New York",
            }],
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
            self.assertEqual(ats.lever("board", commitment="Intern"), [job("intern", "Software Intern") | {"locations": ["Remote"], "url": "https://job/intern"}])

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
            ]),
            [job("a", "Software Engineering Intern"), job("d", "Machine Learning Co-op")],
        )

    def test_internship_us_fallback_handles_board_location_formats(self) -> None:
        source = [
            job("state", "Design Intern") | {"locations": ["Austin, TX"]},
            job("country", "Finance Co-op") | {"locations": ["Remote - United States"]},
            job("foreign", "Design Intern") | {"locations": ["Toronto, Canada"]},
            job("internal", "Internal Tools Engineer") | {"locations": ["Austin, TX"]},
        ]
        self.assertEqual(
            [item["id"] for item in filters.internships_in_us(source)],
            ["state", "country"],
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
            patch.object(watch.notify, "ensure_opted_in"),
            patch.object(watch.notify, "notify_new_job"),
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
                patch.object(watch.notify, "ensure_opted_in"),
                patch.object(watch.notify, "notify_new_job") as notify_new_job,
                patch.object(watch.observability, "log_event"),
            ):
                watch.run()
                notify_new_job.assert_not_called()
                watch.run()

        notify_new_job.assert_called_once_with("Example", newly_posted)


class EmailNotificationTests(unittest.TestCase):
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
