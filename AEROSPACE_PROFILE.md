# Aerospace/mechanical internship profile

This checkout now supports two role profiles:

- `swe_ml` preserves the repository's original U.S. software/ML internship
  behavior.
- `aerospace` watches the supplied aerospace, space, defense, autonomy, and
  advanced-manufacturing target manifest and matches engineering internship
  titles such as mechanical, aerospace, systems, GNC, propulsion, thermal,
  structures, manufacturing, test, controls, robotics, and autonomy.

The aerospace profile currently has 31 working adapters. The first deployed
pilot includes SpaceX, Blue Origin, Northrop Grumman, GE Aerospace, Rocket Lab,
Relativity Space, Firefly Aerospace, Impulse Space, True Anomaly, Apex, Vast,
AeroVironment, Joby Aviation, and BETA Technologies. The remaining names in
`profiles.py` are the watchlist and should be added only after their public
career-board endpoint is identified; a placeholder adapter would cause false
failures and alerts.

## Local pilot

From the directory containing the checkout:

```sh
cp Job-poller/.env.example Job-poller/.env
python -m venv Job-poller/.venv
Job-poller/.venv/bin/pip install -r Job-poller/requirements.txt
```

Set `JOB_POLLER_PROFILE=aerospace` in `.env`. During the first pilot, use
`JOB_POLLER_COMPANIES` to limit the run, for example:

```text
JOB_POLLER_COMPANIES=spacex,blueorigin,northropgrumman,geaerospace,rocketlab,relativityspace,fireflyaerospace,impulsespace,trueanomaly,apexspace,vastspace,aerovironment,jobyaviation,betatechnologies
```

For an email-only pilot, keep `SMS_ALERTS_ENABLED=false` and set:

```text
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-address@gmail.com
SMTP_PASSWORD=your Google app password
EMAIL_TO=your-address@gmail.com
```

`EMAIL_TO` accepts comma-separated recipients. The `.env` file is ignored by
Git; never paste its app password into chat or commit it.

Run an adapter check before enabling alerts. Replace `Job-poller` with the
actual checkout directory name if you cloned it under a different name:

```sh
python -m Job-poller.check --twice spacex
python -m Job-poller.send_test_notification
python -m Job-poller.watch
```

The first successful poll seeds the current postings in `jobs.db`; it does
not send an alert for every existing opening. Later polls alert only on new
stable posting IDs. Failed notifications stay in a durable outbox and are
retried on later runs. A careers source that fails three times in a row sends
one health warning, followed by a recovery message when it works again. A
weekly status message summarizes source health. Keep `SMS_ALERTS_ENABLED=false`
until email results have been reviewed.

## Installed macOS schedule

The local pilot is installed as the LaunchAgent
`com.brendanlyons.aerospace-job-poller` and runs every 30 minutes while the
user is logged in. macOS blocks background agents from opening executables in
Documents, so the editable Git checkout is deployed to:

```text
~/Library/Application Support/AerospaceJobPoller
```

The deployed `.env` and source `.env` both use owner-only permissions. Logs
are written under that Application Support directory in `logs/`. Source-code
changes must be copied to the deployed runtime before they affect scheduled
polls.

After source changes pass tests, deploy them from the checkout with:

```sh
./deploy_macos.sh
```

The deploy command preserves the runtime `jobs.db`, replaces only the code
snapshot, installs declared dependencies, copies `.env` with owner-only
permissions, and reloads the LaunchAgent.
