import JobsTable from './jobs-table';
import { getDashboardJobs } from '../lib/jobs';

function refreshedLabel(value: string | null) {
  if (!value) return 'Refresh time unavailable';
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return 'Refresh time unavailable';
  const formatted = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/Los_Angeles',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  }).format(date).replace(/\bP(?:S|D)T\b/, 'PT');
  return `Last refreshed: ${formatted}`;
}

export default async function Home() {
  const result = await getDashboardJobs();
  return (
    <main>
      <nav className="nav shell">
        <a className="brand" href="#top" aria-label="AeroScout home"><span>AS</span>AeroScout</a>
        <div className="nav-meta"><span className="live-dot" /><span><strong>Private dashboard</strong><time dateTime={result.lastRefreshedAt || undefined}>{refreshedLabel(result.lastRefreshedAt)}</time></span></div>
      </nav>
      <section id="top" className="hero">
        <div className="shell hero-inner">
          <div>
            <p className="eyebrow">AeroScout opportunity index</p>
            <h1>Engineering &amp; STEM<br />Internship Finder</h1>
          </div>
          <dl className="hero-stats">
            <div><dt>{result.sourceCount}</dt><dd>career sources</dd></div>
            <div><dt>1 hr</dt><dd>refresh cycle</dd></div>
            <div><dt>{result.activeJobCount}</dt><dd>active U.S. internships</dd></div>
          </dl>
        </div>
      </section>
      <section className="shell finder"><JobsTable jobs={result.jobs} sources={result.sources} notice={result.notice} isLive={result.source === 'live'} sourceCount={result.sourceCount} healthySourceCount={result.healthySourceCount} warningSourceCount={result.warningSourceCount} lastRefreshedAt={result.lastRefreshedAt} /></section>
      <footer className="shell"><span>AeroScout</span><span>Engineering &amp; STEM internship search.</span></footer>
    </main>
  );
}
