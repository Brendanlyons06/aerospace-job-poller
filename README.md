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

- Runs locally on macOS every 30 minutes with `launchd`.
- Sends Gmail alerts for newly discovered matching postings.
- Supports optional Twilio SMS alerts, disabled by default.
- Has 31 aerospace-profile adapters; the installed pilot enables 14 companies.
- Passed 40 deterministic tests and live two-pass adapter validation when this
  version was prepared.

The installed pilot watches:

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

The complete target manifest is maintained in [`profiles.py`](profiles.py).

## How it works

1. Company adapters read public job listings from each employer's official
   careers system.
2. Structured job-type and location fields are used when the source provides
   them.
3. The aerospace profile keeps U.S. internships with relevant engineering
   titles and excludes unrelated software roles.
4. SQLite stores stable company/job IDs, so the first run seeds existing jobs
   without sending a flood of alerts.
5. Later runs place newly discovered jobs in a durable notification outbox.
6. Failed notifications remain pending and are retried on a later run.

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

## Important files

| File | Purpose |
| --- | --- |
| `profiles.py` | Aerospace target manifest and active role profile |
| `filters.py` | Internship, location, and engineering-title matching |
| `companies/` | One official-careers adapter per company |
| `watch.py` | Concurrent polling, diffing, alerts, and health handling |
| `db.py` | SQLite job history, outbox, and source-health state |
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
