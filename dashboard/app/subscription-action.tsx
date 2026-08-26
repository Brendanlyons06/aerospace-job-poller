'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function SubscriptionAction({ mode, token }: { mode: 'verify' | 'unsubscribe'; token: string }) {
  const [status, setStatus] = useState<'idle' | 'working' | 'done' | 'error'>('idle');
  const label = mode === 'verify' ? 'Confirm email alerts' : 'Unsubscribe';
  async function act() {
    setStatus('working');
    try {
      const response = await fetch(`/api/${mode}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token }),
      });
      const result = await response.json() as { status?: string };
      if (!response.ok || !['confirmed', 'unsubscribed'].includes(result.status || '')) throw new Error(result.status || 'error');
      setStatus('done');
    } catch {
      setStatus('error');
    }
  }
  return (
    <div className="action-card">
      {status === 'done' ? <><h1>{mode === 'verify' ? 'Alerts confirmed' : 'You are unsubscribed'}</h1><p>{mode === 'verify' ? 'Your first digest will arrive on the schedule you selected.' : 'No more AeroScout digests will be sent to this address.'}</p></> : <><h1>{label}</h1><p>{mode === 'verify' ? 'Confirm that you want AeroScout internship digests.' : 'Stop future AeroScout internship digests for this address.'}</p><button type="button" onClick={act} disabled={status === 'working' || !token}>{status === 'working' ? 'Working…' : label}</button>{status === 'error' && <p className="action-error" role="alert">This link is invalid, expired, or temporarily unavailable.</p>}</>}
      <Link href="/">Return to AeroScout</Link>
    </div>
  );
}
