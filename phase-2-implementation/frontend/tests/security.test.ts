// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest, NextResponse } from 'next/server';
vi.mock('server-only', () => ({}));
import { csrfOK, csrfToken, issueLogin, issueSession, loginCsrfOK, session, validPassword } from '../lib/security';
const base = 'http://127.0.0.1:3000';
function request(raw: string, name = 'dd_operator', origin = base) {
  return new NextRequest(base + '/api/assessments', { method:'POST', headers: { Cookie:`${name}=${raw}`, Host:'127.0.0.1:3000', Origin:origin } });
}
beforeEach(() => { process.env.DEALDESK_UI_SESSION_SECRET = 'test-local-session-secret-with-at-least-32-bytes'; process.env.DEALDESK_UI_PASSWORD = 'test-local-password-with-at-least-32-bytes'; });
afterEach(() => { vi.restoreAllMocks(); delete process.env.DEALDESK_UI_SESSION_SECRET; delete process.env.DEALDESK_UI_PASSWORD; });
describe('operator session and CSRF', () => {
  it('signs an HttpOnly Strict session; rejects tampering, expiry and wrong Origin', () => {
    const now = Date.now(); vi.spyOn(Date,'now').mockReturnValue(now);
    const response = NextResponse.json({}); issueSession(response);
    const raw = response.cookies.get('dd_operator')!.value;
    expect(response.headers.get('set-cookie')).toContain('HttpOnly');
    expect(response.headers.get('set-cookie')).toContain('SameSite=strict');
    const nonce = session(request(raw)); expect(nonce).toMatch(/^[0-9a-f]{64}$/);
    expect(csrfOK(new NextRequest(base, { method:'POST', headers:{ Cookie:`dd_operator=${raw}`, Host:'127.0.0.1:3000', Origin:base,'X-CSRF-Token':csrfToken(nonce!) } }), nonce!)).toBe(true);
    expect(csrfOK(request(raw,'dd_operator','http://evil.invalid'), nonce!)).toBe(false);
    expect(session(request(raw.replace(/.$/, raw.at(-1) === '0' ? '1' : '0')))).toBeNull();
    vi.spyOn(Date,'now').mockReturnValue(now + 8*60*60*1000 + 1);
    expect(session(request(raw))).toBeNull();
  });
  it('requires the signed login cookie and rejects incorrect credentials', () => {
    const response = NextResponse.json({}); const token = issueLogin(response);
    const raw = response.cookies.get('dd_login_csrf')!.value;
    const req = new NextRequest(base,{ method:'POST', headers: { Cookie:`dd_login_csrf=${raw}`,Host:'127.0.0.1:3000',Origin:base,'X-CSRF-Token':token } });
    expect(loginCsrfOK(req)).toBe(true);
    expect(loginCsrfOK(request(raw,'dd_login_csrf'))).toBe(false);
    expect(validPassword('test-local-password-with-at-least-32-bytes')).toBe(true);
    expect(validPassword('test-local-password-with-at-least-32-byteZ')).toBe(false);
  });
});
