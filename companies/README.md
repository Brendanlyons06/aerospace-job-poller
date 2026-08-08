# Adding a company

`watch.py` runs one poll loop over every company folder here —
`companies/__init__.py` auto-discovers them, so there's no registry file to
edit. All the shared plumbing — diffing against `jobs.db`, sending the SMS +
email — already lives in `db.py` and `notify.py` and is reused as-is. A new
company only needs to supply jobs (and decide, for itself, what counts as
worth alerting on).

## 0. Check for a hosted board first

Most companies run Greenhouse or Lever, and both have a public JSON API that
`ats.py` already speaks. When that's the case the entire company is four
lines and you can skip everything below except step 4:

```python
from ...ats import greenhouse   # or: lever

COMPANY_NAME = "Anthropic"

def fetch_jobs() -> list[dict]:
    return greenhouse("anthropic")   # board token from boards.greenhouse.io/<token>
```

`ats.py` returns the normalized dicts already. Only write a `client.py` if
the company runs its own bespoke job board — see AGENTS.md for how to
reverse-engineer one from a HAR capture.

## 1. Scaffold the folder

```
companies/<name>/
    __init__.py   # required: the adapter (see below)
    client.py      # optional: raw HTTP/GraphQL calls, if fetch_jobs() isn't trivial
    *.har           # optional: captured requests used to build client.py
```

Any HTTP in `client.py` goes through `http.session()` (or `http.get_json()`)
rather than `requests` directly — `watch.py` fetches companies on a thread
pool it cannot interrupt, so a request without a timeout strands a worker
permanently. `http.session()` supplies one by default.

## 2. Implement the adapter (`companies/<name>/__init__.py`)

Required:

```python
COMPANY_NAME = "Example Corp"

def fetch_jobs() -> list[dict]:
    """Return every open posting, each as:
        {"id": str, "title": str, "locations": list[str], "url": str}
    id must be stable across runs — it's the dedup key in jobs.db.
    """
    ...
```

Optional:

```python
def filter_jobs(jobs: list[dict]) -> list[dict]:
    """Narrow fetch_jobs()'s output down to what's actually worth alerting on."""
    ...
```

**There's no universal filter** — every career site's postings, roles, and
noise look different, so filtering is each company's own call, not something
imposed by `watch.py`. If you omit `filter_jobs`, everything `fetch_jobs()`
returns gets diffed and alerted on as-is. If a company wants filtering, write
whatever logic makes sense for that site — reuse the predicates in
`../filters.py` (`is_us_job`, `is_phd_title`, or the combined
`us_only_no_phd` helper) if they fit, or write company-specific logic from
scratch.

Look at `companies/metacareers/` as a working example: `client.py` recreates
the site's GraphQL search request, `__init__.py` reshapes the response into
the dict format above, and opts into `filters.us_only_no_phd` because Meta's
search returns non-US and PhD-only roles it doesn't want alerts for.

## 3. Verify

```
python -m careers.check <name> --twice
```

Runs your adapter in isolation — no `jobs.db` writes, no texts — validates
the dict contract, and prints what would have alerted. `--twice` re-fetches
and diffs the id sets to prove your ids are stable; an id derived from list
position or from a mutable field looks fine in one run and then reports the
whole board as new on every poll thereafter. Exits nonzero on failure.

Don't use `python -m careers.watch` for this. It writes to `jobs.db`, and a
company only gets one bootstrap run (below) — spending it on a broken
adapter means the first real alert never fires.

## 4. Done

No registration step — drop the folder in and the next
`python -m careers.watch` run picks it up automatically. Its first run seeds
current postings as "seen" without alerting (see `db.sync_and_get_new`), so
nothing fires until a genuinely new job appears after that.

Adapters run concurrently (12 at a time), so keep yours free of mutable
module-level state, and never write to `jobs.db` or send notifications from
inside it — `watch.py` owns both of those, serially.
