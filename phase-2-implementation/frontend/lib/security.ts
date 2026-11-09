import 'server-only';
import { createHmac, randomBytes, timingSafeEqual } from 'node:crypto';
import { NextRequest, NextResponse } from 'next/server';

const sessionName = 'dd_operator';
const loginName = 'dd_login_csrf';
const ttl = 8 * 60 * 60 * 1000;
// Only the explicitly configured synthetic HTTPS deployment can issue public sessions.
export function publicSyntheticDemo() { return process.env.DEALDESK_PUBLIC_SYNTHETIC_DEMO === '1' && process.env.DEALDESK_UI_ORIGIN === 'https://dealdeskdemo.duckdns.org'; }
function secret() { const value = process.env.DEALDESK_UI_SESSION_SECRET; if (!value || value.length < 32) throw new Error('UI session secret missing'); return value; }
function mac(value: string) { return createHmac('sha256', secret()).update(value).digest('hex'); }
function same(a: string, b: string) { const x = Buffer.from(a); const y = Buffer.from(b); return x.length === y.length && timingSafeEqual(x, y); }
function cookie(value: string, maxAge: number) { return { value, httpOnly: true, sameSite: 'strict' as const, secure: new URL(process.env.DEALDESK_UI_ORIGIN || 'http://127.0.0.1:3000').protocol === 'https:', path: '/', maxAge }; }
function issue(prefix: string) { const payload = `${prefix}.${randomBytes(32).toString('hex')}.${Date.now() + ttl}`; return `${payload}.${mac(payload)}`; }
function validate(raw: string | undefined, prefix: string) {
  if (!raw) return null;
  const parts = raw.split('.');
  if (parts.length !== 4 || parts[0] !== prefix || !/^[0-9a-f]{64}$/.test(parts[1]) || !/^\d{13}$/.test(parts[2]) || !/^[0-9a-f]{64}$/.test(parts[3])) return null;
  const payload = parts.slice(0, 3).join('.');
  return Number(parts[2]) > Date.now() && same(mac(payload), parts[3]) ? parts[1] : null;
}
export function session(request: NextRequest) { return validate(request.cookies.get(sessionName)?.value, 'session'); }
export function originOK(request: NextRequest) {
  const origin = process.env.DEALDESK_UI_ORIGIN || 'http://127.0.0.1:3000';
  return request.headers.get('origin') === origin && request.headers.get('sec-fetch-site') !== 'cross-site' && request.headers.get('host') === new URL(origin).host;
}
export function csrfOK(request: NextRequest, nonce: string) { return originOK(request) && same(request.headers.get('x-csrf-token') || '', mac(`csrf.${nonce}`)); }
export function loginCsrfOK(request: NextRequest) {
  const nonce = validate(request.cookies.get(loginName)?.value, 'login');
  return !!nonce && csrfOK(request, nonce);
}
export function issueLogin(response: NextResponse) {
  const raw = issue('login'); response.cookies.set(loginName, raw, cookie(raw, ttl / 1000));
  return mac(`csrf.${raw.split('.')[1]}`);
}
export function issueSession(response: NextResponse, clearLogin = true) {
  const raw = issue('session'); response.cookies.set(sessionName, raw, cookie(raw, ttl / 1000));
  if (clearLogin) response.cookies.delete(loginName);
  return mac(`csrf.${raw.split('.')[1]}`);
}
export function clearSession(response: NextResponse) { response.cookies.delete(sessionName); }
export function csrfToken(nonce: string) { return mac(`csrf.${nonce}`); }
export function validPassword(input: string) {
  const expected = process.env.DEALDESK_UI_PASSWORD;
  if (!expected || expected.length < 32) throw new Error('Operator password missing');
  return same(input, expected);
}
export function denied(status = 401) { return NextResponse.json({ detail: status === 401 ? 'Operator login required' : 'Request refused' }, { status, headers: { 'Cache-Control': 'no-store' } }); }
