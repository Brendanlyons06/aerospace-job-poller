# AGENTS.md

Guidance for an agent asked to add a new company to this repo. Read this
before touching anything — the detailed adapter contract lives in
`companies/README.md`; this file covers the parts that aren't obvious from
reading the code (how to find the API in the first place, how to verify your
work, and mistakes to avoid).

## What this project is

`watch.py` polls career sites for new job postings and texts/emails the user
when one appears. Run as `python -m careers.watch` from the parent directory
(`/Users/rohankrishnan/Coding`), typically on a cron/launchd schedule.

## Architecture (don't relitigate this)

One poller, many company adapters:

- `watch.py` calls `fetch_jobs()` / `filter_jobs()` / `notify_new_job()` for
  every company in `companies.COMPANIES` — this is shared and you should not
  need to touch it to add a company.
- **Fetching is concurrent, the rest isn't.** `watch.py` fans `fetch_jobs()`
  + `filter_jobs()` out across a `ThreadPoolExecutor` (`MAX_WORKERS = 12`,
  sized by memory — see the comment there), then does the `jobs.db` diff and
  the notifications serially on the main thread. Two consequences for
  adapter code: it must be **thread-safe and free of shared mutable module
  state**, and it must **never write to `jobs.db` or send notifications**
  itself. A failing adapter is caught and logged per-company, so one dead
  site can't take down the other 99.
- `http.py` is the shared curl_cffi session (`http.session()` / `http.get_json()`).
  **Always use it instead of a raw HTTP client** — see "Mistakes to avoid".
- `companies/feeds.py` has ready-made helpers for the hosted ATS platforms
  most companies use — Greenhouse, Lever, Ashby, Workday, Phenom — including
  `*_internships_us` variants that apply the US SWE/ML-internship focus this
  poller targets. Check these before reverse-engineering anything.
  (`ats.py` is a deprecated shim kept only for old imports.)
- `companies/__init__.py` auto-discovers every subfolder under `companies/`
  at import time (via `pkgutil`). There is no registry list to hand-edit —
  dropping in a correctly-shaped folder is enough.
- `db.py` dedups by `(company, job_id)` in `jobs.db`. A company's very first
  poll seeds its current postings as "seen" and reports zero new jobs — this
  is intentional, not a bug, so don't add special-casing to work around it.
- `filters.py` is a library of optional predicates (`is_us_job`,
  `is_phd_title`, `us_only_no_phd`). Nothing in it runs automatically —
  **do not add a global filter to `watch.py`**. Filtering is each company's
  own call via an optional `filter_jobs()` in its adapter.

## Adding a company

Full contract and a worked example (`companies/metacareers/`) are in
`companies/README.md` — read that before writing code. Short version:

1. `mkdir companies/<name>`
2. `companies/<name>/__init__.py` exposes `COMPANY_NAME: str` and
   `fetch_jobs() -> list[dict]`, each dict shaped
   `{"id": str, "title": str, "locations": list[str], "url": str}`.
3. If the site's raw API response needs real work to call (auth tokens,
   GraphQL persisted queries, pagination), put that in `companies/<name>/client.py`
   and keep `__init__.py` as a thin adapter that reshapes its output — see
   `companies/metacareers/client.py` vs `companies/metacareers/__init__.py`.
4. Optionally add `filter_jobs(jobs) -> list[dict]` if this company's board
   needs narrowing (wrong region, irrelevant role types, etc). Skip it
   entirely if `fetch_jobs()` already returns exactly what should alert.
5. Nothing to register — auto-discovery picks it up.
6. Verify with `python -m careers.check <name> --twice` (see "Testing").

## Try the easy path first

**Before capturing a single HAR, check whether the company just uses
Greenhouse, Lever, or Ashby.** Most do, and then the whole adapter is:

```python
from ..feeds import greenhouse_internships_us   # or: lever_internships_us,
                                                # ashby_internships_us, ...

COMPANY_NAME = "Anthropic"
CAREERS_URL = "https://www.anthropic.com/careers"

def fetch_jobs() -> list[dict]:
    return greenhouse_internships_us("anthropic")   # the board token
```

The board token is the company slug in `boards.greenhouse.io/<token>`,
`jobs.lever.co/<token>`, or `jobs.ashbyhq.com/<token>` — not a secret. If
the careers page embeds listings in an iframe, the token is usually in the
iframe `src`. Confirm by opening the vendor endpoint in `companies/feeds.py`
with that token substituted in.

This path has no persisted-query id and no CSRF token, so unlike a
hand-built client it doesn't rot when the company rebuilds its frontend.
Prefer it whenever it works. Only fall through to the section below when the
company runs its own bespoke board.

## Finding the API to scrape (when there's no hosted board)

Some career sites (Meta, and most companies large enough to build their own)
don't have a documented public API. The pattern that worked for
`companies/metacareers/`:

1. Open the company's careers/jobs search page in a browser with DevTools
   Network tab open (or use `mcp__claude-in-chrome__*` tools if driving a
   real browser from this session).
2. Perform a search / apply a filter to trigger the actual data-fetching
   request, then export the network capture as a `.har` file.
3. Find the request that returns job listings (often a POST to a GraphQL
   endpoint, sometimes a plain REST GET). Note the URL, required headers
   (auth/CSRF tokens, persisted-query IDs), and the request body shape.
4. Recreate that request in `client.py` using `http.session()`. Expect to
   need an initial GET to pick up cookies/CSRF tokens before the real query
   works (see `get_lsd_token()` in `companies/metacareers/client.py` for the
   pattern — Meta requires a warm-up request before `/graphql` accepts
   anonymous calls).
5. Drop the `.har` file into the company's folder as reference material —
   future re-captures (e.g. when a persisted-query ID rots) start from it.

Persisted-query IDs and CSRF tokens are tied to a site's current frontend
build and *will* eventually 404 or error. If an existing company's adapter
suddenly breaks, re-capture a fresh HAR rather than guessing at the fix.

## Testing your work

- **`python -m careers.check <name> --twice`** from
  `/Users/rohankrishnan/Coding` — this is the one to use on a new adapter.
  It runs `fetch_jobs()`/`filter_jobs()` in isolation, validates the output
  against the dict contract, prints what would have alerted, and exits
  nonzero on failure. It writes nothing and sends nothing. `--twice` fetches
  the board again and diffs the id sets, which is the only way to catch
  unstable ids before they cause a permanent alert storm. With no argument
  it checks every company.
- Do **not** reach for `python -m careers.watch` to test a new adapter — it
  writes to `jobs.db`, so a broken adapter silently burns that company's
  one-time bootstrap seeding and the real first alert never fires. Run it
  once `check` is green.
- `python -m careers.send_test_notification` — sends a hardcoded sample job
  through the real `notify.py` path (SMS + email) without needing a live
  company at all. Use this to isolate notify-path issues from adapter
  issues.
- Requires `.env` populated (see `.env.example`) for SMS/email to actually
  send — Twilio creds for text, Gmail SMTP app-password creds for email.
  Without them, `fetch_jobs()`/`filter_jobs()`/dedup logic can still be
  tested directly in a REPL even if notification sending would fail.

## Mistakes to avoid

- Don't add a manual entry to any "registry" — there isn't one anymore;
  auto-discovery in `companies/__init__.py` handles it.
- Don't hand-roll a client for a company that's already on Greenhouse,
  Lever, or Ashby — check `companies/feeds.py` first.
- **Don't call an HTTP client directly — use `http.session()`.** A request with
  no timeout hangs its pool thread forever, and a stuck thread can't be
  killed from outside, so one dark career site would permanently consume a
  worker slot. `http.session()` applies a default timeout (plus retries and
  a browser UA) so you can't forget.
- Don't keep module-level mutable state in an adapter, and don't write to
  `jobs.db` or send notifications from `fetch_jobs()` — adapters run
  concurrently on a thread pool.
- Don't make `job["id"]` anything derived from position-in-list or a hash of
  mutable fields (like title) — it must be stable across polls or every run
  will look like a brand new posting.
- Don't apply US-only/no-PhD filtering by default "to be safe" — that's
  Meta-specific behavior living in Meta's own `filter_jobs`, not a global
  rule.
- Don't hardcode secrets in adapter code — anything credential-shaped goes
  in `.env` (see existing `TWILIO_*`/`SMTP_*` vars for the pattern), even if
  a given company's API happens not to need auth today.
