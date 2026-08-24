import JobsTable from './jobs-table';
import { getDashboardJobs } from '../lib/jobs';

export default async function Home() {
  const result = await getDashboardJobs();
  return (
    <main>
      <nav className="nav shell">
        <a className="brand" href="#top" aria-label="AeroScout home"><span>AS</span>AeroScout</a>
        <div className="nav-meta"><span className="live-dot" />Private dashboard</div>
      </nav>
      <section id="top" className="hero">
        <div className="shell hero-inner">
          <div>
            <p className="eyebrow">Aerospace internship intelligence</p>
            <h1>Find the work that<br />moves flight forward.</h1>
            <p className="hero-copy">One focused view of early-career engineering roles across aerospace, defense, space, and advanced manufacturing.</p>
          </div>
          <dl className="hero-stats">
            <div><dt>50</dt><dd>career sources</dd></div>
            <div><dt>1 hr</dt><dd>refresh cycle</dd></div>
            <div><dt>U.S.</dt><dd>internships</dd></div>
          </dl>
        </div>
      </section>
      <section className="shell finder"><JobsTable jobs={result.jobs} notice={result.notice} isLive={result.source === 'live'} /></section>
      <footer className="shell"><span>AeroScout</span><span>Built for focused engineering searches.</span></footer>
    </main>
  );
}
