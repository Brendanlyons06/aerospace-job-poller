import { NextRequest, NextResponse } from 'next/server';
import { callSupabaseRpc } from '../../../lib/supabase-rpc';

const allowedFrequency = new Set(['daily', 'weekly']);

function optional(value: unknown, maxLength = 100) {
  return typeof value === 'string' && value.trim() ? value.trim().slice(0, maxLength) : null;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as Record<string, unknown>;
    const email = typeof body.email === 'string' ? body.email.trim().slice(0, 254) : '';
    const frequency = typeof body.frequency === 'string' && allowedFrequency.has(body.frequency) ? body.frequency : 'daily';
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      return NextResponse.json({ accepted: false, message: 'Enter a valid email address.' }, { status: 400 });
    }
    await callSupabaseRpc('request_email_subscription', {
      p_email: email,
      p_frequency: frequency,
      p_discipline: optional(body.discipline),
      p_sector: optional(body.sector),
      p_company: optional(body.company),
      p_state: optional(body.state, 2),
      p_website: optional(body.website),
    });
    return NextResponse.json({ accepted: true });
  } catch {
    return NextResponse.json(
      { accepted: false, message: 'Alerts are temporarily unavailable. Please try again later.' },
      { status: 503 },
    );
  }
}
