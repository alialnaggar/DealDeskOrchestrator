import { NextRequest, NextResponse } from 'next/server';
import { create, BackendError } from '@/lib/backend';
import { csrfOK, denied, publicSyntheticDemo, session } from '@/lib/security';
import { allowScenarioLaunch } from '@/lib/launch-limit';
export async function POST(request: NextRequest) {
  const nonce = session(request); if (!nonce) return denied();
  if (!csrfOK(request, nonce) || request.headers.get('content-type')?.split(';')[0] !== 'application/json' || Number(request.headers.get('content-length') || 0) > 512) return denied(403);
  try {
    const reader = request.body?.getReader(); if (!reader) return denied(400);
    const chunks: Uint8Array[] = []; let size = 0;
    for (;;) {
      const { done, value } = await reader.read(); if (done) break;
      size += value.byteLength;
      if (size > 512) { await reader.cancel(); return denied(413); }
      chunks.push(value);
    }
    const body = JSON.parse(new TextDecoder().decode(Buffer.concat(chunks)));
    const key = request.headers.get('idempotency-key') || '';
    if (!body || Array.isArray(body) || Object.keys(body).length !== 1 || !['B01/RC01','N01/UC02'].includes(body.scenario) || !/^[A-Za-z0-9_-]{8,128}$/.test(key)) return denied(400);
    if (publicSyntheticDemo() && !allowScenarioLaunch(nonce, key)) return NextResponse.json({ detail: 'Synthetic demo launch limit reached. Try again later; do not replay a running assessment.' }, { status: 429, headers: { 'Cache-Control': 'no-store', 'Retry-After': '60' } });
    const result = await create(body.scenario, key);
    return NextResponse.json(result, { status: 202, headers: { 'Cache-Control': 'no-store' } });
  } catch (err) { return NextResponse.json({ detail: err instanceof BackendError ? err.message : 'Invalid request' }, { status: err instanceof BackendError ? err.status : 400, headers: { 'Cache-Control': 'no-store' } }); }
}
