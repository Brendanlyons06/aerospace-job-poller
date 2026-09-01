'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type { DashboardJob, DashboardSource } from '../lib/jobs';
import MultiStateSelect from './multi-state-select';
import SubscriptionForm from './subscription-form';

const PAGE_SIZE = 25;

const labels: Record<string, string> = {
  'aerospace-defense': 'Aerospace & defense',
  'space-launch-spacecraft': 'Space & launch',
  'advanced-aircraft-autonomy': 'Aircraft & autonomy',
  'advanced-manufacturing-hardware': 'Manufacturing & hardware',
  'engineering-organization': 'Research & government',
  'other-engineering': 'Other engineering',
  gnc: 'GNC',
  'flight-controls': 'Flight controls',
  'flight-test': 'Flight test',
  'flight-sciences': 'Flight sciences',
  'aircraft-performance': 'Aircraft performance',
  'systems-integration-test': 'Systems integration & test',
  'mechanical-design': 'Mechanical design',
  'data-science': 'Data science & AI',
  'physics-research': 'Physics & research',
  'supply-chain': 'Supply chain',
  'on-site': 'On-site',
  remote: 'Remote',
  hybrid: 'Hybrid',
};

function label(value: string | null | undefined, fallback = 'Not classified') {
  if (!value) return fallback;
  return labels[value] || value.replace(/-/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function timestamp(value: string | null | undefined) {
  if (!value) return 0;
  const parsed = new Date(value).getTime();
  return Number.isFinite(parsed) ? parsed : 0;
}

function ageLabel(value: string, referenceTime: number) {
  const elapsed = referenceTime - new Date(value).getTime();
  if (!Number.isFinite(elapsed) || elapsed < 0) return 'Recently';
  const days = Math.floor(elapsed / 86_400_000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).format(new Date(value));
}

function prefixedAgeLabel(prefix: string, value: string, referenceTime: number) {
  return `${prefix} ${ageLabel(value, referenceTime).toLowerCase()}`;
}

function closingLabel(value: string | null, referenceTime: number) {
  if (!value) return null;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return null;
  const days = Math.ceil((date.getTime() - referenceTime) / 86_400_000);
  if (days < 0) return 'Deadline passed';
  if (days === 0) return 'Closes today';
  if (days <= 14) return `Closes in ${days} ${days === 1 ? 'day' : 'days'}`;
  return `Closes ${new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }).format(date)}`;
}

function checkedLabel(value: string | null, referenceTime: number) {
  if (!value) return 'Not checked yet';
  return `Checked ${ageLabel(value, referenceTime).toLowerCase()}`;
}

function jobKey(job: DashboardJob) {
  return `${job.company}::${job.jobId}`;
}

function distanceMiles(a: { latitude: number; longitude: number }, b: { latitude: number; longitude: number }) {
  const radians = (degrees: number) => degrees * Math.PI / 180;
  const latitudeDelta = radians(b.latitude - a.latitude);
  const longitudeDelta = radians(b.longitude - a.longitude);
  const value = Math.sin(latitudeDelta / 2) ** 2
    + Math.cos(radians(a.latitude)) * Math.cos(radians(b.latitude)) * Math.sin(longitudeDelta / 2) ** 2;
  return 3958.8 * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
}

type JobsTableProps = {
  jobs: DashboardJob[];
  sources: DashboardSource[];
  notice: string;
  isLive: boolean;
  sourceCount: number;
  healthySourceCount: number;
  warningSourceCount: number;
  lastRefreshedAt: string | null;
  subscriberCount: number;
  subscriberCap: number;
};

export default function JobsTable({ jobs, sources, notice, isLive, sourceCount, healthySourceCount, warningSourceCount, lastRefreshedAt, subscriberCount, subscriberCap }: JobsTableProps) {
  const [query, setQuery] = useState('');
  const [discipline, setDiscipline] = useState('all');
  const [sector, setSector] = useState('all');
  const [company, setCompany] = useState('all');
  const [workMode, setWorkMode] = useState('all');
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [freshness, setFreshness] = useState('all');
  const [sort, setSort] = useState('newest');
  const [page, setPage] = useState(1);
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [savedOnly, setSavedOnly] = useState(false);
  const [position, setPosition] = useState<{ latitude: number; longitude: number } | null>(null);
  const [radius, setRadius] = useState(50);
  const [geoMessage, setGeoMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onShortcut = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onShortcut);
    return () => window.removeEventListener('keydown', onShortcut);
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        const saved = JSON.parse(window.localStorage.getItem('aeroscout-saved-jobs') || '[]');
        if (Array.isArray(saved)) setSavedJobs(new Set(saved.filter((item): item is string => typeof item === 'string')));
      } catch {
        setSavedJobs(new Set());
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const referenceTime = timestamp(lastRefreshedAt) || Math.max(0, ...jobs.map((job) => timestamp(job.firstSeen)));

  const options = useMemo(() => ({
    disciplines: [...new Set(jobs.map((job) => job.discipline).filter((item): item is string => Boolean(item)))].sort((a, b) => label(a).localeCompare(label(b))),
    sectors: [...new Set(jobs.map((job) => job.sector).filter((item): item is string => Boolean(item)))].sort((a, b) => label(a).localeCompare(label(b))),
    companies: [...new Set(jobs.map((job) => job.company))].sort(),
    workModes: [...new Set(jobs.map((job) => job.workMode).filter((item): item is string => Boolean(item)))].sort((a, b) => label(a).localeCompare(label(b))),
    states: [...new Set(jobs.flatMap((job) => job.locationStates))].sort(),
  }), [jobs]);

  const filteredJobs = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const maxAge = freshness === 'all' ? null : Number(freshness) * 86_400_000;
    const filtered = jobs.filter((job) => {
      const searchable = [job.title, job.company, job.fullLocation, label(job.discipline), label(job.sector), label(job.workMode)].filter(Boolean).join(' ').toLowerCase();
      const discoveredAt = timestamp(job.firstSeen);
      const discoveredAge = referenceTime - discoveredAt;
      const inRadius = !position || job.locationCoordinates.some((coordinates) => distanceMiles(position, coordinates) <= radius);
      const inSelectedLocation = selectedStates.length === 0 || selectedStates.some((selected) => (
        selected === 'REMOTE' ? job.workMode === 'remote' : job.locationStates.includes(selected)
      ));
      return (discipline === 'all' || job.discipline === discipline)
        && (sector === 'all' || job.sector === sector)
        && (company === 'all' || job.company === company)
        && (workMode === 'all' || job.workMode === workMode)
        && inSelectedLocation
        && (maxAge === null || (discoveredAt > 0 && discoveredAge >= 0 && discoveredAge <= maxAge))
        && (!savedOnly || savedJobs.has(jobKey(job)))
        && inRadius
        && (!needle || searchable.includes(needle));
    });

    return filtered.sort((a, b) => {
      if (sort === 'company') return a.company.localeCompare(b.company) || a.title.localeCompare(b.title);
      if (sort === 'posted') return timestamp(b.postedAt || b.firstSeen) - timestamp(a.postedAt || a.firstSeen);
      if (sort === 'closing') {
        const aClose = timestamp(a.closesAt) || Number.MAX_SAFE_INTEGER;
        const bClose = timestamp(b.closesAt) || Number.MAX_SAFE_INTEGER;
        return aClose - bClose || timestamp(b.firstSeen) - timestamp(a.firstSeen);
      }
      return timestamp(b.firstSeen) - timestamp(a.firstSeen);
    });
  }, [company, discipline, freshness, jobs, position, query, radius, referenceTime, savedJobs, savedOnly, sector, selectedStates, sort, workMode]);

  const pageCount = Math.max(1, Math.ceil(filteredJobs.length / PAGE_SIZE));
  const visibleJobs = filteredJobs.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const filtersActive = Boolean(query || discipline !== 'all' || sector !== 'all' || company !== 'all' || workMode !== 'all' || selectedStates.length || freshness !== 'all' || savedOnly || position);
  const attentionSources = sources.filter((source) => source.status === 'degraded' || source.status === 'failing');
  const orderedSources = [...sources].sort((a, b) => {
    const priority = { failing: 0, degraded: 1, pending: 2, 'no-open-roles': 3, healthy: 4 };
    return priority[a.status] - priority[b.status] || a.company.localeCompare(b.company);
  });

  const clearFilters = () => {
    setQuery(''); setDiscipline('all'); setSector('all'); setCompany('all');
    setWorkMode('all'); setSelectedStates([]); setFreshness('all'); setSort('newest'); setSavedOnly(false); setPosition(null); setGeoMessage(''); setPage(1);
  };

  const toggleSaved = (job: DashboardJob) => {
    const key = jobKey(job);
    setSavedJobs((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key); else next.add(key);
      window.localStorage.setItem('aeroscout-saved-jobs', JSON.stringify([...next]));
      return next;
    });
  };

  const useLocation = () => {
    if (!navigator.geolocation) { setGeoMessage('Location filtering is not supported by this browser.'); return; }
    setGeoMessage('Requesting your location…');
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => { setPosition({ latitude: coords.latitude, longitude: coords.longitude }); setGeoMessage('Radius filter active for jobs with map coordinates.'); setPage(1); },
      () => setGeoMessage('Location permission was not granted.'),
      { enableHighAccuracy: false, timeout: 10_000 },
    );
  };

  return (
    <>
      <div className="section-heading">
        <div><p className="eyebrow dark">Internship finder</p><h2>Current opportunities</h2></div>
      </div>

      <SubscriptionForm
        disciplines={options.disciplines.map((value) => ({ value, label: label(value) }))}
        sectors={options.sectors.map((value) => ({ value, label: label(value) }))}
        companies={options.companies}
        states={options.states}
        subscriberCount={subscriberCount}
        subscriberCap={subscriberCap}
      />

      <details className={`source-health ${warningSourceCount ? 'attention' : ''}`}>
        <summary>
          <span className="health-copy"><span className="live-dot" /><span><strong>{healthySourceCount} of {sourceCount} sources responding</strong><small>{warningSourceCount ? `${warningSourceCount} ${warningSourceCount === 1 ? 'source needs' : 'sources need'} attention` : 'All monitored career sources are responding'}</small></span></span>
          <span className="health-action">View source health</span>
        </summary>
        <div className="source-grid">
          {orderedSources.map((source) => (
            <div className="source-row" key={source.company}>
              <span className={`status-dot ${source.status}`} />
              <span><strong>{source.company}</strong><small>{label(source.sector)} · {checkedLabel(source.checkedAt, referenceTime)}</small></span>
              <span className={`source-status ${source.status}`}>{source.status === 'no-open-roles' ? 'No roles' : label(source.status)}</span>
            </div>
          ))}
          {!sources.length && <p className="source-empty">Source-level status will appear after the next live poll.</p>}
        </div>
        {attentionSources.length > 0 && <p className="health-footnote">A degraded source is retried automatically. One source failure never stops the remaining companies from refreshing.</p>}
      </details>

      <div className="search-row">
        <label className="search">
          <span aria-hidden="true">⌕</span>
          <input ref={inputRef} value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} type="search" placeholder="Search title, company, location, or discipline" aria-label="Search internships" />
          <kbd>⌘ K</kbd>
        </label>
        <label className="sort-control"><span>Sort</span><select value={sort} onChange={(event) => { setSort(event.target.value); setPage(1); }}><option value="newest">Recently discovered</option><option value="posted">Newest posted</option><option value="closing">Closing soon</option><option value="company">Company A–Z</option></select></label>
      </div>

      <div className="filter-panel" aria-label="Internship filters">
        <label className="filter-field"><span>Discipline</span><select value={discipline} onChange={(event) => { setDiscipline(event.target.value); setPage(1); }}><option value="all">All disciplines</option>{options.disciplines.map((item) => <option value={item} key={item}>{label(item)}</option>)}</select></label>
        <label className="filter-field"><span>Sector</span><select value={sector} onChange={(event) => { setSector(event.target.value); setPage(1); }}><option value="all">All sectors</option>{options.sectors.map((item) => <option value={item} key={item}>{label(item)}</option>)}</select></label>
        <label className="filter-field"><span>Company</span><select value={company} onChange={(event) => { setCompany(event.target.value); setPage(1); }}><option value="all">All companies</option>{options.companies.map((item) => <option value={item} key={item}>{item}</option>)}</select></label>
        <label className="filter-field"><span>Work mode</span><select value={workMode} onChange={(event) => { setWorkMode(event.target.value); setPage(1); }}><option value="all">Any work mode</option>{options.workModes.map((item) => <option value={item} key={item}>{label(item)}</option>)}</select></label>
        <div className="filter-field"><span>States &amp; remote</span><MultiStateSelect values={selectedStates} options={[{ value: 'REMOTE', label: 'Remote / location-independent' }, ...options.states.map((item) => ({ value: item, label: item }))]} onChange={(values) => { setSelectedStates(values); setPage(1); }} allLabel="All locations" /></div>
        <label className="filter-field"><span>Discovered</span><select value={freshness} onChange={(event) => { setFreshness(event.target.value); setPage(1); }}><option value="all">Any time</option><option value="1">Past 24 hours</option><option value="3">Past 3 days</option><option value="7">Past week</option><option value="14">Past 2 weeks</option><option value="30">Past month</option></select></label>
        <button className="clear-filters" type="button" onClick={clearFilters} disabled={!filtersActive}>Reset filters</button>
      </div>

      <div className="personal-tools">
        <button className={savedOnly ? 'active' : ''} type="button" onClick={() => { setSavedOnly((value) => !value); setPage(1); }}>★ Saved on this device ({savedJobs.size})</button>
        <button className={position ? 'active' : ''} type="button" onClick={position ? () => { setPosition(null); setGeoMessage(''); } : useLocation}>{position ? 'Clear radius' : 'Use my location'}</button>
        <label><span>Within</span><select value={radius} onChange={(event) => { setRadius(Number(event.target.value)); setPage(1); }} disabled={!position}><option value="25">25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option><option value="250">250 miles</option></select></label>
        {geoMessage && <small role="status">{geoMessage}</small>}
      </div>

      <div className="results-bar" aria-live="polite">
        <span className="result-count">{filteredJobs.length} matching {filteredJobs.length === 1 ? 'role' : 'roles'}</span>
      </div>

      <div className="table-wrap">
        <table>
          <thead><tr><th>Company &amp; position</th><th>Discipline</th><th>Location</th><th>Work mode</th><th>Timing</th><th><span className="sr-only">Apply</span></th></tr></thead>
          <tbody>
            {visibleJobs.map((job) => {
              const closes = closingLabel(job.closesAt, referenceTime);
              const postedDiffersFromDiscovery = Boolean(
                job.postedAt && Math.abs(timestamp(job.firstSeen) - timestamp(job.postedAt)) >= 86_400_000,
              );
              return (
                <tr key={`${job.company}-${job.jobId}`}>
                  <td><button className={`save-job ${savedJobs.has(jobKey(job)) ? 'saved' : ''}`} type="button" onClick={() => toggleSaved(job)} aria-label={`${savedJobs.has(jobKey(job)) ? 'Remove' : 'Save'} ${job.title}`}>★</button><span className="company-mark">{job.company.slice(0, 2).toUpperCase()}</span><span><strong>{job.title}</strong><small>{job.company} · {label(job.sector)}</small></span></td>
                  <td><span className="tag">{label(job.discipline, 'Engineering')}</span></td>
                  <td className="location-cell"><span title={job.fullLocation}>{job.location}</span></td>
                  <td><span className="mode-label">{label(job.workMode, 'Not listed')}</span></td>
                  <td className="timing-cell">
                    <span>{prefixedAgeLabel('Found', job.firstSeen, referenceTime)}</span>
                    {postedDiffersFromDiscovery && job.postedAt && <small className="posted-age">{prefixedAgeLabel('Posted', job.postedAt, referenceTime)}</small>}
                    {closes && <small className={closes === 'Deadline passed' ? 'deadline-passed' : ''}>{closes}</small>}
                  </td>
                  <td>{job.url ? <a className="arrow" href={job.url} target="_blank" rel="noreferrer" aria-label={`Apply for ${job.title} at ${job.company}`}>↗</a> : <span className="arrow disabled" aria-hidden="true">↗</span>}</td>
                </tr>
              );
            })}
            {filteredJobs.length === 0 && <tr><td className="empty" colSpan={6}><strong>No matching internships</strong><small>Try removing a filter or using a broader search.</small></td></tr>}
          </tbody>
        </table>
      </div>

      {pageCount > 1 && <nav className="pagination" aria-label="Opportunity pages"><button type="button" disabled={page === 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Previous</button><span>Page {page} of {pageCount}</span><button type="button" disabled={page === pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>Next</button></nav>}
      <p className={`data-note ${isLive ? '' : 'preview'}`}><span className="live-dot" />{notice}</p>
    </>
  );
}
