import { NextRequest, NextResponse } from 'next/server';
import { csrfToken, issueLogin, session } from '@/lib/security';
export const dynamic = 'force-dynamic';
export async function GET(request: NextRequest) {
  const response = NextResponse.json({ csrf: '' }, { headers: { 'Cache-Control': 'no-store' } });
  const token = session(request);
  const csrf = token ? csrfToken(token) : issueLogin(response);
  return NextResponse.json({ csrf, authenticated: !!token }, { headers: { 'Cache-Control': 'no-store', 'Set-Cookie': response.headers.get('set-cookie') || '' } });
}
