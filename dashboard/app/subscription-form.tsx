'use client';

import { FormEvent, useState } from 'react';
import MultiStateSelect from './multi-state-select';

type Option = { value: string; label: string };
type Props = {
  disciplines: Option[];
  sectors: Option[];
  companies: string[];
  states: string[];
  subscriberCount: number;
  subscriberCap: number;
};

export default function SubscriptionForm({ disciplines, sectors, companies, states, subscriberCount, subscriberCap }: Props) {
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [showManage, setShowManage] = useState(false);
  const [manageEmail, setManageEmail] = useState('');
  const [manageStatus, setManageStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [manageMessage, setManageMessage] = useState('');

  const stateOptions = [
    { value: 'REMOTE', label: 'Remote / location-independent' },
    ...states.map((item) => ({ value: item, label: item })),
  ];

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    setStatus('sending');
    setMessage('');
    const form = new FormData(formElement);
    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...Object.fromEntries(form.entries()), states: selectedStates }),
      });
      const result = await response.json() as { accepted?: boolean; message?: string };
      if (!response.ok || !result.accepted) throw new Error(result.message || 'Unable to subscribe');
      setStatus('sent');
      setMessage('Request received. If this address still needs verification, a confirmation email will arrive within about an hour. If it is already subscribed, its existing alerts remain active.');
      formElement.reset();
      setSelectedStates([]);
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'Alerts are temporarily unavailable.');
    }
  }

  async function requestManagement(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setManageStatus('sending');
    setManageMessage('');
    try {
      const response = await fetch('/api/request-management', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: manageEmail }),
      });
      const result = await response.json() as { accepted?: boolean; message?: string };
      if (!response.ok || !result.accepted) throw new Error(result.message || 'Unable to request a link');
      setManageStatus('sent');
      setManageMessage('If that address has an active subscription, its private management link will arrive within about an hour.');
    } catch (error) {
      setManageStatus('error');
      setManageMessage(error instanceof Error ? error.message : 'Management links are temporarily unavailable.');
    }
  }

  return (
    <section className="subscribe-card" aria-labelledby="subscribe-heading">
      <div className="subscribe-intro">
        <p className="eyebrow dark">Free email alerts</p>
        <h3 id="subscribe-heading">Let new internships come to you.</h3>
        <p>Choose a daily or weekly digest delivered around 9:15 AM Pacific. Filters are optional, and every address must be verified.</p>
        <small>{subscriberCount} of {subscriberCap} free beta subscriptions active</small>
        <button className="manage-link-toggle" type="button" onClick={() => setShowManage((value) => !value)}>{showManage ? 'Hide management request' : 'Manage subscription'}</button>
        {showManage && <form className="manage-link-request" onSubmit={requestManagement}>
          <label><span>Email</span><input type="email" required autoComplete="email" value={manageEmail} onChange={(event) => setManageEmail(event.target.value)} placeholder="you@example.com" /></label>
          <button type="submit" disabled={manageStatus === 'sending'}>{manageStatus === 'sending' ? 'Requesting…' : 'Email my private link'}</button>
          {manageMessage && <p className={`subscribe-message ${manageStatus}`} role="status">{manageMessage}</p>}
        </form>}
      </div>
      <form className="subscribe-form" onSubmit={submit}>
        <label className="subscribe-email"><span>Email</span><input type="email" name="email" required autoComplete="email" placeholder="you@example.com" /></label>
        <label><span>Frequency</span><select name="frequency" defaultValue="daily"><option value="daily">Daily digest</option><option value="weekly">Weekly digest</option></select></label>
        <label><span>Discipline</span><select name="discipline" defaultValue=""><option value="">All disciplines</option>{disciplines.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label><span>Sector</span><select name="sector" defaultValue=""><option value="">All sectors</option>{sectors.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label><span>Company</span><select name="company" defaultValue=""><option value="">All companies</option>{companies.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <div className="state-select-label"><span>States &amp; remote</span><MultiStateSelect values={selectedStates} options={stateOptions} onChange={setSelectedStates} allLabel="All locations" /></div>
        <label className="website-field" aria-hidden="true"><span>Website</span><input name="website" tabIndex={-1} autoComplete="off" /></label>
        <button type="submit" disabled={status === 'sending'}>{status === 'sending' ? 'Requesting…' : 'Subscribe free'}</button>
        {message && <p className={`subscribe-message ${status}`} role="status">{message}</p>}
        <p className="subscribe-terms">Unsubscribe or manage preferences from any digest. By subscribing, you agree to the <a href="/terms">Terms</a> and acknowledge the <a href="/privacy">Privacy policy</a>.</p>
      </form>
    </section>
  );
}
