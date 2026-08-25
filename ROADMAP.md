# Product roadmap

The project is being developed as a low-cost internship discovery and
notification service. The early phases use free infrastructure; paid services
are introduced only when usage or SMS delivery requires them.

## Foundation — complete

- Aerospace/mechanical/systems internship title profile
- Durable job deduplication and notification retries
- Gmail alerts and optional disabled-by-default SMS support
- Per-company health monitoring and weekly summaries
- 50 relevant adapters enabled in the free cloud poller
- Local macOS scheduler and private GitHub repository

## Phase 1 — free cloud poller

- Hourly GitHub Actions schedule with a manual test mode
- Supabase PostgreSQL persistence with versioned migrations
- Cloud fail-safe that prohibits temporary SQLite fallback
- Encrypted GitHub Secrets and explicit schedule activation
- Two consecutive real cloud polls confirming persistence and deduplication
  before retiring the Mac scheduler

## Phase 2 — dashboard-ready data — complete

- Separate company-sector and job-discipline classifications
- Posted, closing, first-seen, last-seen, and closed dates
- Structured city/state locations and geographic coordinates
- Remote/hybrid/on-site and compensation fields when published

Implemented with backward-compatible SQLite upgrades and Supabase migration
`002_dashboard_ready_data.sql`. A posting closes after two consecutive
successful polls no longer return it, limiting false closures from transient
career-board inconsistencies.

## Phase 3 — company expansion — complete

- Validate and enable the 17 existing relevant adapters outside the pilot
- Add major aerospace/defense employers
- Add high-priority new-space companies
- Add aircraft, industrial, laboratory, and government sources
- Prefer 50–60 reliable sources before chasing complete list coverage

The enabled set now contains 50 official sources. It combines the original
14-company pilot, the 17 previously inactive aerospace adapters, and 19 new
adapters across defense, spacecraft, aircraft, and advanced manufacturing.
New sources are baseline-seeded before they can alert, preventing a backlog
of already-open internships from being emailed during the expansion.

## Phase 4 — searchable dashboard

- [x] Private AeroScout dashboard foundation
- [x] Current-job table backed by a restricted Supabase read view
- [x] Keyword search, discipline shortcuts, and direct application links
- [x] Last-completed-poll freshness indicator
- [x] Normalized, deduplicated, compact multi-location display
- [x] Safe per-source health status and aggregate active-role metrics
- [x] Sector, company, date, work-mode, and state filters
- [ ] Radius-based geographic search
- [x] Pagination and sorting

The first dashboard slice is implemented in `dashboard/`. It displays a safe
preview when its two Supabase settings are absent and automatically switches
to the live active-job feed when they are present. The database exposes only
job-listing fields, aggregate metrics, and non-sensitive source status;
notification records, raw source errors, and poller-control tables remain
inaccessible.

## Phase 5 — accounts and email subscriptions

- Authentication, saved searches, and verified email addresses
- Immediate, daily, and weekly notification frequencies
- Filter-matched subscriptions, delivery history, and unsubscribe controls

## Phase 6 — opt-in SMS

- Verified phone numbers, explicit consent, quiet hours, and STOP handling
- Delivery caps and compliant provider integration
- SMS remains disabled until its unavoidable provider costs are approved

## Phase 7 — production hardening

- Adapter monitoring, backups, administration tools, and security review
- Privacy and usage policies
- Public beta and paid-infrastructure decision based on measured demand
