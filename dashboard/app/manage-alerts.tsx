'use client';

/* eslint-disable @next/next/no-html-link-for-pages -- native navigation avoids the hosted router interception bug */

import { FormEvent, useEffect, useState } from 'react';
import MultiStateSelect from './multi-state-select';

type Option = { value: string; label: string };
type Preferences = {
  frequency: 'daily' | 'weekly';
  discipline: string;
  sector: string;
  company: string;
  state: string;
  states: string[];
};

const emptyPreferences: Preferences = { frequency: 'daily', discipline: '', sector: '', company: '', state: '', states: [] };

export default function ManageAlerts({ token, disciplines, sectors, companies, states }: {
  token: string;
  disciplines: Option[];
  sectors: Option[];
  companies: string[];
  states: string[];
}) {
  const [preferences, setPreferences] = useState<Preferences>(emptyPreferences);
  const [subscriptionStatus, setSubscriptionStatus] = useState<'active' | 'unsubscribed' | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'saving' | 'saved' | 'deleting' | 'deleted' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    let active = true;
    async function load() {
      if (!token) { setStatus('error'); setMessage('This manage-alerts link is missing its private token.'); return; }
      try {
        const response = await fetch('/api/manage', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'load', token }),
        });
        const result = await response.json() as Partial<Preferences> & { status?: string };
        if (!response.ok || !['active', 'unsubscribed'].includes(result.status || '')) throw new Error();
        if (!active) return;
        setPreferences({
          frequency: result.frequency === 'weekly' ? 'weekly' : 'daily',
          discipline: result.discipline || '', sector: result.sector || '', company: result.company || '',
          state: result.state || '',
          states: Array.isArray(result.states) ? result.states : (result.state ? [result.state] : []),
        });
        setSubscriptionStatus(result.status as 'active' | 'unsubscribed');
        setStatus('ready');
      } catch {
        if (active) { setStatus('error'); setMessage('This manage-alerts link is invalid or the subscription is no longer active.'); }
      }
    }
    load();
    return () => { active = false; };
  }, [token]);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setStatus('saving'); setMessage('');
    try {
      const response = await fetch('/api/manage', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'update', token, ...preferences }),
      });
      const result = await response.json() as { status?: string };
      if (!response.ok || result.status !== 'updated') throw new Error();
      setStatus('saved'); setMessage('Your alert schedule and filters are updated.');
    } catch {
      setStatus('error'); setMessage('Your changes could not be saved. The link may no longer be active.');
    }
  }

  async function deleteData() {
    if (!window.confirm('Permanently delete this email subscription and all of its alert settings? This cannot be undone.')) return;
    setStatus('deleting'); setMessage('');
    try {
      const response = await fetch('/api/manage', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete', token }),
      });
      const result = await response.json() as { status?: string };
      if (!response.ok || result.status !== 'deleted') throw new Error();
      setStatus('deleted'); setMessage('Your email subscription and alert settings were permanently deleted.');
    } catch {
      setStatus('error'); setMessage('Your subscription data could not be deleted. The link may no longer be active.');
    }
  }

  if (status === 'loading') return <div className="action-card"><h1>Manage alerts</h1><p>Loading your private alert settings…</p></div>;
  if (status === 'deleted') return <div className="action-card"><h1>Data deleted</h1><p>{message}</p><a href="/">Return to AeroScout</a></div>;
  if (status === 'error' && message.startsWith('This manage-alerts link')) {
    return <div className="action-card"><h1>Manage alerts</h1><p className="action-error">{message}</p><a href="/">Return to AeroScout</a></div>;
  }
  if (subscriptionStatus === 'unsubscribed') {
    return <div className="action-card manage-card"><p className="eyebrow dark">Private subscription settings</p><h1>Alerts are unsubscribed</h1><p>No more digests will be delivered. You can keep this inactive record or permanently remove the email address and its alert settings.</p><div className="danger-zone"><strong>Delete my alert data</strong><p>This action cannot be undone.</p><button type="button" onClick={deleteData} disabled={status === 'deleting'}>{status === 'deleting' ? 'Deleting…' : 'Delete permanently'}</button></div>{message && <p className="manage-message error" role="status">{message}</p>}<a href="/">Return to AeroScout</a></div>;
  }

  const optionWithCurrent = (items: Option[], current: string) => current && !items.some((item) => item.value === current)
    ? [{ value: current, label: current }, ...items] : items;
  const stringWithCurrent = (items: string[], current: string) => current && !items.includes(current) ? [current, ...items] : items;
  const stateOptions = [
    { value: 'REMOTE', label: 'Remote / location-independent' },
    ...[...new Set([...states, ...preferences.states.filter((item) => item !== 'REMOTE')])].sort().map((item) => ({ value: item, label: item })),
  ];

  return (
    <div className="action-card manage-card">
      <p className="eyebrow dark">Private subscription settings</p>
      <h1>Manage alerts</h1>
      <p>Choose when your digest arrives and narrow it to the internships you care about.</p>
      <form className="manage-form" onSubmit={save}>
        <label><span>Frequency</span><select value={preferences.frequency} onChange={(event) => setPreferences({ ...preferences, frequency: event.target.value as Preferences['frequency'] })}><option value="daily">Daily — about 9:15 AM PT</option><option value="weekly">Weekly — Mondays about 9:15 AM PT</option></select></label>
        <label><span>Discipline</span><select value={preferences.discipline} onChange={(event) => setPreferences({ ...preferences, discipline: event.target.value })}><option value="">All disciplines</option>{optionWithCurrent(disciplines, preferences.discipline).map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label><span>Sector</span><select value={preferences.sector} onChange={(event) => setPreferences({ ...preferences, sector: event.target.value })}><option value="">All sectors</option>{optionWithCurrent(sectors, preferences.sector).map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label><span>Company</span><select value={preferences.company} onChange={(event) => setPreferences({ ...preferences, company: event.target.value })}><option value="">All companies</option>{stringWithCurrent(companies, preferences.company).map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <div className="manage-state-select"><span>States &amp; remote</span><MultiStateSelect values={preferences.states} options={stateOptions} onChange={(values) => setPreferences({ ...preferences, states: values, state: values[0] || '' })} allLabel="All locations" /></div>
        <button type="submit" disabled={status === 'saving' || status === 'deleting'}>{status === 'saving' ? 'Saving…' : 'Save preferences'}</button>
      </form>
      {message && <p className={`manage-message ${status === 'saved' ? 'success' : 'error'}`} role="status">{message}</p>}
      <div className="danger-zone"><strong>Delete my alert data</strong><p>This permanently removes the email address and all subscription settings connected to this private link.</p><button type="button" onClick={deleteData} disabled={status === 'deleting'}>{status === 'deleting' ? 'Deleting…' : 'Delete permanently'}</button></div>
      <a href="/">Return to AeroScout</a>
    </div>
  );
}
