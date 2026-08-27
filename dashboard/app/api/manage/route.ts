import { NextRequest, NextResponse } from 'next/server';
import { callSupabaseRpc } from '../../../lib/supabase-rpc';

const allowedFrequency = new Set(['daily', 'weekly']);

function tokenValue(value: unknown) {
  return typeof value === 'string' ? value.trim().slice(0, 80) : '';
}

function optional(value: unknown, maxLength = 100) {
  return typeof value === 'string' && value.trim() ? value.trim().slice(0, maxLength) : null;
}

function selectedStates(value: unknown) {
  if (!Array.isArray(value)) return [];
  return [...new Set(value
    .filter((item): item is string => typeof item === 'string')
    .map((item) => item.trim().toUpperCase())
    .filter((item) => item === 'REMOTE' || /^[A-Z]{2}$/.test(item)))]
    .slice(0, 64);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as Record<string, unknown>;
    const action = typeof body.action === 'string' ? body.action : '';
    const token = tokenValue(body.token);
    if (!token) return NextResponse.json({ status: 'invalid' }, { status: 400 });

    if (action === 'load') {
      const subscription = await callSupabaseRpc('get_email_subscription', { p_token: token });
      return NextResponse.json(subscription);
    }
    if (action === 'delete') {
      const status = await callSupabaseRpc('delete_email_subscription', { p_token: token });
      return NextResponse.json({ status });
    }
    if (action === 'update') {
      const frequency = typeof body.frequency === 'string' && allowedFrequency.has(body.frequency)
        ? body.frequency
        : '';
      if (!frequency) return NextResponse.json({ status: 'invalid' }, { status: 400 });
      const status = await callSupabaseRpc('update_email_subscription', {
        p_token: token,
        p_frequency: frequency,
        p_discipline: optional(body.discipline),
        p_sector: optional(body.sector),
        p_company: optional(body.company),
        p_states: selectedStates(body.states),
      });
      return NextResponse.json({ status });
    }
    return NextResponse.json({ status: 'invalid' }, { status: 400 });
  } catch {
    return NextResponse.json({ status: 'unavailable' }, { status: 503 });
  }
}
