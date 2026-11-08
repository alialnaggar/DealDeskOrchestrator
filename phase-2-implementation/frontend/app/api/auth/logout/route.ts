import { NextRequest, NextResponse } from 'next/server';
import { clearSession, csrfOK, denied, session } from '@/lib/security';
export async function POST(request: NextRequest) {
  const nonce = session(request);
  if (!nonce) return denied();
  if (!csrfOK(request, nonce)) return denied(403);
  const response = NextResponse.json({ authenticated: false }, { headers: { 'Cache-Control': 'no-store' } });
  clearSession(response);
  return response;
}
