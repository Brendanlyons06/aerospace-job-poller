'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type { DashboardJob } from '../lib/jobs';

const preferredDisciplines = ['Mechanical', 'Aerospace', 'Systems', 'GNC & Controls'];

function ageLabel(value: string) {
  const elapsed = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(elapsed) || elapsed < 0) return 'Recently';
  const days = Math.floor(elapsed / 86_400_000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date(value));
}

export default function JobsTable({ jobs, notice, isLive }: { jobs: DashboardJob[]; notice: string; isLive: boolean }) {
  const [query, setQuery] = useState('');
  const [discipline, setDiscipline] = useState('All disciplines');
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

  const disciplines = useMemo(() => {
    const available = new Set(jobs.map((job) => job.discipline).filter(Boolean));
    const ordered = preferredDisciplines.filter((item) => available.has(item));
    const remaining = [...available].filter((item): item is string => Boolean(item) && !ordered.includes(item as string)).sort();
    return ['All disciplines', ...ordered, ...remaining];
  }, [jobs]);

  const filteredJobs = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return jobs.filter((job) => {
      const matchesDiscipline = discipline === 'All disciplines' || job.discipline === discipline;
      const searchable = [job.title, job.company, job.fullLocation, job.discipline, job.sector, job.workMode].filter(Boolean).join(' ').toLowerCase();
      return matchesDiscipline && (!needle || searchable.includes(needle));
    });
  }, [discipline, jobs, query]);

  return (
    <>
      <div className="section-heading">
        <div><p className="eyebrow dark">Internship finder</p><h2>Current opportunities</h2></div>
        <span className="result-count">{filteredJobs.length} {filteredJobs.length === 1 ? 'role' : 'roles'} shown</span>
      </div>
      <label className="search">
        <span aria-hidden="true">⌕</span>
        <input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} type="search" placeholder="Search title, company, location, or discipline" aria-label="Search internships" />
        <kbd>⌘ K</kbd>
      </label>
      <div className="pills" aria-label="Filter by discipline">
        {disciplines.map((item) => <button key={item} className={discipline === item ? 'active' : ''} onClick={() => setDiscipline(item)}>{item}</button>)}
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Company &amp; position</th><th>Discipline</th><th>Location</th><th>Discovered</th><th><span className="sr-only">Apply</span></th></tr></thead>
          <tbody>
            {filteredJobs.map((job) => (
              <tr key={`${job.company}-${job.jobId}`}>
                <td><span className="company-mark">{job.company.slice(0, 2).toUpperCase()}</span><span><strong>{job.title}</strong><small>{job.company}</small></span></td>
                <td><span className="tag">{job.discipline || 'Engineering'}</span></td>
                <td className="location-cell"><span title={job.fullLocation}>{job.location}</span></td><td>{ageLabel(job.postedAt || job.firstSeen)}</td>
                <td>{job.url ? <a className="arrow" href={job.url} target="_blank" rel="noreferrer" aria-label={`Apply for ${job.title} at ${job.company}`}>↗</a> : <span className="arrow disabled" aria-hidden="true">↗</span>}</td>
              </tr>
            ))}
            {filteredJobs.length === 0 && <tr><td className="empty" colSpan={5}><strong>No matching internships</strong><small>Try a broader keyword or choose all disciplines.</small></td></tr>}
          </tbody>
        </table>
      </div>
      <p className={`data-note ${isLive ? '' : 'preview'}`}><span className="live-dot" />{notice}</p>
    </>
  );
}
