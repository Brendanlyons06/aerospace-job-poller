'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';

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

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus('sending');
    setMessage('');
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(form.entries())),
      });
      const result = await response.json() as { accepted?: boolean; message?: string };
      if (!response.ok || !result.accepted) throw new Error(result.message || 'Unable to subscribe');
      setStatus('sent');
      setMessage('Check your inbox within about an hour and confirm your address. No alerts are sent until you confirm.');
      event.currentTarget.reset();
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'Alerts are temporarily unavailable.');
    }
  }

  return (
    <section className="subscribe-card" aria-labelledby="subscribe-heading">
      <div className="subscribe-intro">
        <p className="eyebrow dark">Free email alerts</p>
        <h3 id="subscribe-heading">Let new internships come to you.</h3>
        <p>Choose a daily or weekly digest delivered around 9:15 AM Pacific. Filters are optional, and every address must be verified.</p>
        <small>{subscriberCount} of {subscriberCap} free beta subscriptions active</small>
      </div>
      <form className="subscribe-form" onSubmit={submit}>
        <label className="subscribe-email"><span>Email</span><input type="email" name="email" required autoComplete="email" placeholder="you@example.com" /></label>
        <label><span>Frequency</span><select name="frequency" defaultValue="daily"><option value="daily">Daily digest</option><option value="weekly">Weekly digest</option></select></label>
        <label><span>Discipline</span><select name="discipline" defaultValue=""><option value="">All disciplines</option>{disciplines.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label><span>Sector</span><select name="sector" defaultValue=""><option value="">All sectors</option>{sectors.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
        <label><span>Company</span><select name="company" defaultValue=""><option value="">All companies</option>{companies.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <label><span>State</span><select name="state" defaultValue=""><option value="">All states</option>{states.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <label className="website-field" aria-hidden="true"><span>Website</span><input name="website" tabIndex={-1} autoComplete="off" /></label>
        <button type="submit" disabled={status === 'sending'}>{status === 'sending' ? 'Requesting…' : 'Subscribe free'}</button>
        {message && <p className={`subscribe-message ${status}`} role="status">{message}</p>}
        <p className="subscribe-terms">Unsubscribe or manage preferences from any digest. By subscribing, you agree to the <Link href="/terms">Terms</Link> and acknowledge the <Link href="/privacy">Privacy policy</Link>.</p>
      </form>
    </section>
  );
}
