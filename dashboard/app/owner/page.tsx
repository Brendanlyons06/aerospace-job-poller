import { headers } from 'next/headers';
import { getOwnerStatus, type OwnerStatus } from '../../lib/owner';

export const dynamic = 'force-dynamic';

const workflowBase = 'https://github.com/Brendanlyons06/aerospace-job-poller/actions/workflows';

function timestamp(value: string | null) {
  if (!value) return 'Not recorded yet';
  const parsed = new Date(value);
  if (!Number.isFinite(parsed.getTime())) return 'Not recorded yet';
  return new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Los_Angeles', month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit', timeZoneName: 'short',
  }).format(parsed).replace(/\bP(?:S|D)T\b/, 'PT');
}

function statusCopy(status: OwnerStatus['pollStatus'], age: number | null) {
  if (status === 'healthy') return `Healthy · ${age ?? 0} minutes since the last poll`;
  if (status === 'delayed') return `Delayed · ${age ?? 0} minutes since the last poll`;
  if (status === 'stale') return `Stale · ${age ?? 0} minutes since the last poll`;
  return 'Poll status is unavailable';
}

function OwnerNav() {
  return <nav className="owner-nav shell"><a className="brand" href="/"><span>AS</span>AeroScout</a><a href="/">Return to dashboard</a></nav>;
}

function MessageCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <main className="owner-page"><OwnerNav /><section className="owner-message"><p className="eyebrow dark">Owner console</p><h1>{title}</h1>{children}</section></main>;
}

export default async function OwnerPage() {
  const requestHeaders = await headers();
  const visitorId = requestHeaders.get('oai-authenticated-user-id');
  const visitorEmail = requestHeaders.get('oai-authenticated-user-email');
  const ownerId = process.env.AEROSCOUT_OWNER_USER_ID;

  if (!visitorId) {
    return <MessageCard title="Owner sign-in required"><p>Sign in with ChatGPT to open AeroScout’s private operating status.</p><a className="owner-primary" href="/signin-with-chatgpt?return_to=%2Fowner" target="_top">Sign in with ChatGPT</a></MessageCard>;
  }
  if (!ownerId || visitorId !== ownerId) {
    return <MessageCard title="Owner access only"><p>This signed-in account is not authorized to view AeroScout’s operating controls.</p><a className="owner-secondary" href="/">Return to AeroScout</a></MessageCard>;
  }

  const status = await getOwnerStatus();
  if (!status) {
    return <MessageCard title="Status data unavailable"><p>The owner page is protected correctly, but its aggregate status view is not reachable yet. Try again after the next poll completes.</p><a className="owner-secondary" href="/owner">Try again</a></MessageCard>;
  }

  return (
    <main className="owner-page">
      <OwnerNav />
      <section className="owner-shell shell">
        <header className="owner-heading"><div><p className="eyebrow dark">Private operations</p><h1>AeroScout owner console</h1><p>Signed in as {visitorEmail || 'the authorized owner'}.</p></div><div className={`owner-health ${status.pollStatus}`}><span className={`live-dot ${status.pollStatus}`} /><strong>{statusCopy(status.pollStatus, status.pollAgeMinutes)}</strong><small>Last poll: {timestamp(status.lastPollAt)}</small></div></header>

        <section className="owner-metrics" aria-label="AeroScout operating metrics">
          <article><span>Active jobs</span><strong>{status.activeJobCount}</strong><small>across {status.sourceCount} sources</small></article>
          <article><span>Active subscribers</span><strong>{status.activeSubscribers}</strong><small>{status.pendingSubscribers} awaiting verification · cap {status.subscriberCap}</small></article>
          <article><span>Source warnings</span><strong>{status.warningSourceCount}</strong><small>{status.warningSourceCount ? 'needs review' : 'all responding normally'}</small></article>
          <article><span>Email usage today</span><strong>{status.emailsSentToday}</strong><small>of {status.dailyEmailCap} safety limit</small></article>
        </section>

        <div className="owner-columns">
          <section className="owner-panel"><h2>Scheduled workers</h2><dl className="owner-schedule"><div><dt>Career-site poll</dt><dd>{timestamp(status.lastPollAt)}</dd></div><div><dt>Digest worker</dt><dd>{timestamp(status.lastDigestAt)}</dd></div><div><dt>Latest subscriber digest</dt><dd>{timestamp(status.latestSubscriberDigestAt)}</dd></div><div><dt>Next due subscriber</dt><dd>{timestamp(status.nextSubscriberDigestAt)}</dd></div></dl><div className="owner-actions"><a href={`${workflowBase}/hourly-poller.yml`} target="_blank" rel="noreferrer">Open poll controls ↗</a><a href={`${workflowBase}/daily-digest.yml`} target="_blank" rel="noreferrer">Open digest controls ↗</a><a href={`${workflowBase}/poll-watchdog.yml`} target="_blank" rel="noreferrer">Open recovery watchdog ↗</a></div><p className="owner-note">Manual runs open in GitHub and require your GitHub sign-in, keeping workflow credentials out of this website.</p></section>

          <section className="owner-panel"><h2>Source attention</h2>{status.warningSources.length ? <div className="owner-warning-list">{status.warningSources.map((source) => <div key={source.company}><span className={`status-dot ${source.status}`} /><span><strong>{source.company}</strong><small>{source.consecutiveFailures} consecutive failure{source.consecutiveFailures === 1 ? '' : 's'} · checked {timestamp(source.checkedAt)}</small></span></div>)}</div> : <div className="owner-all-clear"><span className="live-dot" /><strong>All tracked sources are responding normally.</strong></div>}<p className="owner-note">Subscriber records remain private. This console only shows counts and delivery health.</p></section>
        </div>
      </section>
    </main>
  );
}
