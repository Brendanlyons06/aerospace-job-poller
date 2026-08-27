import { NextRequest, NextResponse } from 'next/server';
import { callSupabaseRpc } from '../../../lib/supabase-rpc';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as Record<string, unknown>;
    const token = typeof body.token === 'string' ? body.token.slice(0, 80) : '';
    if (!token) return NextResponse.json({ status: 'invalid' }, { status: 400 });
    const result = await callSupabaseRpc('confirm_email_subscription_with_controls', { p_token: token });
    return NextResponse.json(result);
  } catch {
    return NextResponse.json({ status: 'unavailable' }, { status: 503 });
  }
}
