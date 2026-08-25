# Aerospace Job Poller

A local job-alert service for U.S. aerospace, mechanical, systems, flight,
propulsion, manufacturing, test, controls, robotics, and autonomy engineering
internships.

This project is a derivative of
[`rohankrishnan2000/Job-poller`](https://github.com/rohankrishnan2000/Job-poller),
which was originally built to watch software and machine-learning internships.
The aerospace profile, company adapters, durable notifications, health
monitoring, Gmail support, tests, and macOS deployment workflow were added for
this version.

## Current status

- Runs hourly for free in GitHub Actions with Supabase PostgreSQL persistence.
- The previous macOS `launchd` scheduler is disabled but preserved as a
  rollback option.
- Sends Gmail alerts for newly discovered matching postings.
- Supports optional Twilio SMS alerts, disabled by default.
- Has 50 enabled aerospace-profile adapters using official career sources.
- Stores dashboard-ready sectors, disciplines, lifecycle dates, structured
  locations, work modes, and source-published compensation/date metadata.
- Passes deterministic tests and live two-pass adapter validation.

The enabled set includes:

- SpaceX
- Blue Origin
- Northrop Grumman
- GE Aerospace
- Rocket Lab
- Relativity Space
- Firefly Aerospace
- Impulse Space
- True Anomaly
- Apex
- Vast
- AeroVironment
- Joby Aviation
- BETA Technologies
- RTX, BAE Systems, Leidos, Anduril, Shield AI, and Stoke Space
- Varda, K2 Space, The Aerospace Corporation, Zipline, and Astranis
- Epirus, CACI, Mach Industries, Skydio, Hadrian, and Saronic
- Planet Labs, Archer Aviation, Muon Space, Machina Labs, and Gravitics
- Northwood Space, Axiom Space, Loft Orbital, Wisk Aero, and Boom Supersonic
- Sierra Nevada Corporation, Moog, Curtiss-Wright, and Applied Materials
- ispace, Apple Hardware Engineering, Caterpillar, Astrolab, and Starpath

The complete target manifest is maintained in [`profiles.py`](profiles.py).

## How it works

1. Company adapters read public job listings from each employer's official
   careers system.
2. Structured job-type and location fields are used when the source provides
   them.
3. The aerospace profile keeps U.S. internships with relevant engineering
   titles and excludes unrelated software roles.
4. SQLite locally or Supabase PostgreSQL in the cloud stores stable
   company/job IDs, so the first run seeds existing jobs without sending a
   flood of alerts.
5. Later runs place newly discovered jobs in a durable notification outbox.
6. Failed notifications remain pending and are retried on a later run.

## Dashboard-ready data

Phase 2 keeps company classification separate from job classification. For
example, SpaceX is in the `space-launch-spacecraft` sector while one of its
jobs can be classified as `propulsion`, `mechanical-design`, or `systems`.

The persistence layer now maintains:

- Company name, adapter slug, sector, and official careers URL
- Job discipline, employment type, work mode, application URL, and raw title
- Source-published posting and closing dates when available
- First-seen, last-seen, and closed dates observed by the poller
- Compensation range, currency, and period when published by the source
- One structured row per location with label, city, state, country, and
  optional source-provided latitude/longitude

A posting is marked closed after it is absent from two consecutive successful
polls. This avoids turning a one-hour board inconsistency into a false closure.
Existing SQLite and Supabase databases upgrade in place; no job history or
notification state is discarded.

Career-source failures are isolated: one unavailable company does not stop the
other companies from being checked. The service sends one warning after three
consecutive failures, a recovery notice when the source works again, and a
weekly health summary.

## Local setup

Python 3.11 or newer is recommended.

From the directory containing this checkout:

```sh
python3 -m venv job-poller/.venv
job-poller/.venv/bin/pip install -r job-poller/requirements.txt
cp job-poller/.env.example job-poller/.env
```

Edit `.env` and set at least:

```text
JOB_POLLER_PROFILE=aerospace
JOB_POLLER_COMPANIES=spacex,blueorigin,northropgrumman,geaerospace

EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-address@gmail.com
SMTP_PASSWORD=your-google-app-password
EMAIL_TO=your-address@gmail.com

SMS_ALERTS_ENABLED=false
```

For Gmail, enable two-step verification and use a Google App Password rather
than the normal account password. Never commit `.env`; it is intentionally
ignored by Git.

## Validate and run

Run commands from the directory containing the checkout. Replace `job-poller`
with the actual checkout folder name if needed.

```sh
# Deterministic test suite
job-poller/.venv/bin/python -m unittest discover -s job-poller/tests -v

# Read-only live validation; does not update the database or send alerts
job-poller/.venv/bin/python -m job-poller.check --twice

# Verify Gmail/Twilio configuration with a test notification
job-poller/.venv/bin/python -m job-poller.send_test_notification

# Run one real polling cycle
job-poller/.venv/bin/python -m job-poller.watch
```

Live adapter tests are opt-in because career sites change independently:

```sh
RUN_LIVE_POLL_TESTS=1 \
  job-poller/.venv/bin/python -m unittest \
  job-poller.tests.test_live_polling -v
```

## macOS background schedule

The included deployment helper installs a per-user `launchd` agent that runs
every 30 minutes:

```sh
cd job-poller
./deploy_macos.sh
```

The deployed runtime lives at:

```text
~/Library/Application Support/AerospaceJobPoller
```

Deployment preserves the runtime database and copies `.env` with owner-only
permissions. Logs are stored inside the runtime's `logs` directory. The
checked-in LaunchAgent currently contains the local macOS account path and
should be adjusted if installed under a different account.

See [`AEROSPACE_PROFILE.md`](AEROSPACE_PROFILE.md) for the profile and local
deployment notes, and [`companies/README.md`](companies/README.md) for the
adapter contract.

## Free cloud schedule

The checked-in GitHub Actions workflow runs all 50 enabled sources hourly at
17 minutes past the hour. It uses Supabase PostgreSQL for durable state and
refuses to poll if the database secret is missing, preventing accidental use
of a temporary runner-local database.

Follow [`CLOUD_SETUP.md`](CLOUD_SETUP.md) to create the free Supabase project,
add the four encrypted GitHub Secrets, send a cloud test email, and run the
first poll. The hourly schedule remains dormant until the `POLLER_ENABLED`
repository variable is explicitly set to `true`. Keep the Mac scheduler
disabled while GitHub Actions is active to prevent duplicate polling. The
local service files remain available for rollback.

The planned company expansion, dashboard, subscription, and SMS phases are
tracked in [`ROADMAP.md`](ROADMAP.md).

## Private AeroScout dashboard

Phase 4 includes a responsive current-opportunity table with keyword search,
discipline, sector, company, work-mode, state, and discovery-date filters;
sorting, pagination, closing-date labels, source-health status, and direct
application links. The Engineering & STEM Internship Finder reads active
postings through restricted Supabase views. Migrations
`004_dashboard_locations_and_status.sql` and
`005_dashboard_health_and_metrics.sql` add structured locations, poll
freshness, aggregate metrics, and safe source statuses. Raw errors,
notification history, and poller-control data remain inaccessible.

Copy `dashboard/.env.example` to `dashboard/.env.local` and fill in:

```text
SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
SUPABASE_ANON_KEY=YOUR-SUPABASE-PUBLISHABLE-OR-ANON-KEY
```

Use only the Supabase publishable/anon key here, never the database password or
service-role key. Without these settings, the dashboard intentionally displays
clearly labeled preview data.

## Important files

| File | Purpose |
| --- | --- |
| `profiles.py` | Aerospace target manifest and active role profile |
| `job_metadata.py` | Dashboard sectors, disciplines, locations, and optional metadata |
| `filters.py` | Internship, location, and engineering-title matching |
| `companies/` | One official-careers adapter per company |
| `watch.py` | Concurrent polling, diffing, alerts, and health handling |
| `db.py` | SQLite/PostgreSQL job history, outbox, and source-health state |
| `supabase/migrations/` | Versioned cloud database schema |
| `dashboard/` | Private AeroScout searchable dashboard |
| `.github/workflows/hourly-poller.yml` | Free hourly cloud schedule |
| `notify.py` | Gmail and optional Twilio delivery |
| `check.py` | Read-only adapter and stable-ID validation |
| `deploy_macos.sh` | Safe macOS runtime deployment |

## Security and privacy

The following local files must never be committed and are covered by
`.gitignore`:

- `.env`
- `jobs.db`
- `.sms_opt_in_sent`
- `.job-poller.lock`
- `logs/`
- `.venv/`

The poller reads public career listings and stores only normalized job titles,
locations, stable posting IDs, URLs, delivery status, and source-health data.

## Upstream and redistribution

The upstream repository is credited above and remains configured as the
historical source of this derivative. No license file was present in the
upstream checkout when this version was prepared. Keep derivative repositories
private unless the upstream author grants permission to redistribute the code.
