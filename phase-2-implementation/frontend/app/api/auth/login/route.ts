import { NextRequest, NextResponse } from 'next/server';
import { denied, issueSession, loginCsrfOK, publicSyntheticDemo, validPassword } from '@/lib/security';
export async function POST(request: NextRequest) {
  if (publicSyntheticDemo()) return denied(404);
  if (!loginCsrfOK(request) || request.headers.get('content-type')?.split(';')[0] !== 'application/json' || Number(request.headers.get('content-length') || 0) > 512) return denied(403);
  let password: unknown;
  try { const text = await request.text(); if (text.length > 512) return denied(413); const body = JSON.parse(text); if (!body || Array.isArray(body) || Object.keys(body).length !== 1) return denied(400); password = body.password; } catch { return denied(400); }
  if (typeof password !== 'string' || password.length > 256 || !validPassword(password)) return denied();
  const response = NextResponse.json({ authenticated: true }, { headers: { 'Cache-Control': 'no-store' } });
  issueSession(response);
  return response;
}
