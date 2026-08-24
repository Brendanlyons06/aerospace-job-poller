# Free cloud setup: GitHub Actions and Supabase

This deployment runs one poll every hour without requiring a continuously
running server. Local macOS polling remains available as a fallback.

## 1. Create the free Supabase project

1. Sign in at <https://supabase.com/dashboard> and create a new project.
2. Save the database password in a password manager. Do not put it in Git,
   an issue, a screenshot, or a chat message.
3. Wait for the project to finish provisioning.
4. Open **Connect**, choose the PostgreSQL connection string, and select the
   **Transaction pooler** URI. Replace the password placeholder if needed.
5. Keep the completed URI private. The app creates its tables automatically
   on the first successful poll.

The transaction pooler URI generally uses port `6543`. Use the exact value
shown by Supabase rather than constructing it by hand.

If the database password contains symbols such as `@`, `:`, `/`, `#`, `%`,
or `=`, percent-encode the password portion of the URI. Supabase documents
this requirement in its PostgreSQL role and password guide.

## 2. Add four encrypted GitHub secrets

Open the private repository on GitHub, then go to:

**Settings → Secrets and variables → Actions → New repository secret**

Create these secrets one at a time:

| Secret | Value |
| --- | --- |
| `SUPABASE_DATABASE_URL` | Complete Supabase transaction-pooler URI |
| `SMTP_USER` | Gmail address that sends the alerts |
| `SMTP_PASSWORD` | 16-character Google App Password |
| `EMAIL_TO` | Address that should receive alerts |

Spaces can be removed from the displayed Google App Password. Never use the
normal Gmail password.

## 3. Test from GitHub

1. Open the repository's **Actions** tab.
2. Select **Hourly Aerospace Job Poller**.
3. Choose **Run workflow**.
4. Select `test-notification` and run it. Confirm the test email arrives.
5. Run it again with `poll` selected.
6. Open the run log. A healthy first poll includes:
   - `database backend: postgresql`
   - results for the 50 enabled companies
   - a final `polled .../50 companies` summary
7. After both manual tests pass, return to **Settings → Secrets and variables
   → Actions**, open the **Variables** tab, and create `POLLER_ENABLED` with
   the value `true`. This activates the hourly schedule.

The first cloud poll establishes a baseline and intentionally does not email
every internship that was already open. Future newly discovered postings do
generate alerts.

## 4. Validate before disabling the Mac scheduler

Run two consecutive real cloud polls and confirm both use the PostgreSQL
backend. The first establishes or updates the Supabase state; the second must
finish with no duplicate notifications. Once both pass, disable the Mac
scheduler to avoid two independent pollers racing to notify for the same jobs.
For a more conservative cutover, observing normal hourly runs for 24–48 hours
is still an option, but it is not technically required.

## Cost guardrails

- Keep the GitHub repository private.
- Keep the schedule hourly (`17 * * * *`).
- Keep `POLLER_ENABLED` unset until both manual tests pass.
- In <https://github.com/settings/billing>, enable the included-usage alerts
  for 90% and 100%. If the billing UI offers an Actions hard-stop budget,
  enable **Stop usage when budget limit is reached**.
- Review database usage in the Supabase dashboard.

The workflow uses no paid Render service, persistent disk, SMS provider, or
continuous virtual machine.

## Troubleshooting

- **Missing secret:** confirm all four names match exactly.
- **No scheduled runs:** confirm the repository variable `POLLER_ENABLED` is
  exactly `true`.
- **Database connection error:** recopy the transaction-pooler URI and verify
  its password. Do not paste the URI into an issue or workflow log.
- **No job email on the first poll:** expected baseline behavior.
- **A company fails:** other companies still complete; the poller warns after
  three consecutive failures.
- **Test email works but polling fails:** inspect the database line first; the
  workflow refuses to fall back to temporary SQLite storage.
