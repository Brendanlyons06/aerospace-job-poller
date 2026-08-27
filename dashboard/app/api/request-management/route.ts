import { NextRequest, NextResponse } from 'next/server';
import { callSupabaseRpc } from '../../../lib/supabase-rpc';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as Record<string, unknown>;
    const email = typeof body.email === 'string' ? body.email.trim().slice(0, 254) : '';
    const website = typeof body.website === 'string' ? body.website.trim().slice(0, 200) : null;
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      return NextResponse.json({ accepted: false, message: 'Enter a valid email address.' }, { status: 400 });
    }
    await callSupabaseRpc('request_subscription_management', {
      p_email: email,
      p_website: website,
    });
    return NextResponse.json({ accepted: true });
  } catch {
    return NextResponse.json(
      { accepted: false, message: 'Management links are temporarily unavailable. Please try again later.' },
      { status: 503 },
    );
  }
}
