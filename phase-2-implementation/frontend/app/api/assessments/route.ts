import { NextRequest, NextResponse } from 'next/server';
import { create, BackendError } from '@/lib/backend';
import { csrfOK, denied, session } from '@/lib/security';
export async function POST(request: NextRequest) {
  const nonce = session(request); if (!nonce) return denied();
  if (!csrfOK(request, nonce) || request.headers.get('content-type')?.split(';')[0] !== 'application/json' || Number(request.headers.get('content-length') || 0) > 512) return denied(403);
  try {
    const text = await request.text(); if (text.length > 512) return denied(413);
    const body = JSON.parse(text);
    const key = request.headers.get('idempotency-key') || '';
    if (!body || Array.isArray(body) || Object.keys(body).length !== 1 || !['B01/RC01','N01/UC02'].includes(body.scenario) || !/^[A-Za-z0-9_-]{8,128}$/.test(key)) return denied(400);
    const result = await create(body.scenario, key);
    return NextResponse.json(result, { status: 202, headers: { 'Cache-Control': 'no-store' } });
  } catch (err) { return NextResponse.json({ detail: err instanceof BackendError ? err.message : 'Invalid request' }, { status: err instanceof BackendError ? err.status : 400, headers: { 'Cache-Control': 'no-store' } }); }
}
