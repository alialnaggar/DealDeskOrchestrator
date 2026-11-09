// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
vi.mock('server-only', () => ({}));
vi.mock('../lib/backend', () => ({ create: vi.fn(), BackendError: class BackendError extends Error { status = 502; } }));
import { create } from '../lib/backend';
import { GET as sessionToken } from '../app/api/auth/csrf/route';
import { POST as launch } from '../app/api/assessments/route';
import { POST as passwordLogin } from '../app/api/auth/login/route';
import { createLaunchLimiter } from '../lib/launch-limit';
import { publicSyntheticDemo } from '../lib/security';

const origin = 'https://dealdeskdemo.duckdns.org';
beforeEach(() => {
  process.env.DEALDESK_UI_ORIGIN = origin;
  process.env.DEALDESK_PUBLIC_SYNTHETIC_DEMO = '1';
  process.env.DEALDESK_UI_SESSION_SECRET = 'private-test-secret-at-least-thirty-two-characters';
  vi.mocked(create).mockResolvedValue({ version:'demo-api-v1', assessment_id:'a'.repeat(32), scenario:'B01/RC01', mode:'offline_scripted',status:'accepted',last_sequence:0,phase1c_pin:'pin',created:true });
});
afterEach(() => {
  vi.clearAllMocks();
  for (const key of ['DEALDESK_UI_ORIGIN','DEALDESK_PUBLIC_SYNTHETIC_DEMO','DEALDESK_UI_SESSION_SECRET']) delete process.env[key];
});

describe('isolated public synthetic demo', () => {
  it('requires an exact HTTPS deployment origin to enable passwordless access', () => {
    expect(publicSyntheticDemo()).toBe(true);
    process.env.DEALDESK_UI_ORIGIN = 'http://127.0.0.1:3000';
    expect(publicSyntheticDemo()).toBe(false);
  });
  it('issues a Secure signed session and CSRF token without a password but rejects unrestricted creation', async () => {
    const response = await sessionToken(new NextRequest(origin+'/api/auth/csrf'));
    const body = await response.json();
    const cookie = response.cookies.get('dd_operator')?.value;
    expect(body.authenticated).toBe(true);
    expect(body.csrf).toMatch(/^[0-9a-f]{64}$/);
    expect(cookie).toBeTruthy();
    expect(response.headers.get('set-cookie')).toContain('Secure');
    const post = (scenario: string, host = 'dealdeskdemo.duckdns.org') => new NextRequest(origin+'/api/assessments', {method:'POST',headers:{Host:host,Origin:origin,Cookie:`dd_operator=${cookie}`,'Content-Type':'application/json','X-CSRF-Token':body.csrf,'Idempotency-Key':'synthetic-key-123'},body:JSON.stringify({scenario})});
    expect((await launch(post('arbitrary/customer'))).status).toBe(400);
    expect((await launch(post('B01/RC01','evil.invalid'))).status).toBe(403);
    expect((await launch(new NextRequest(origin+'/api/assessments',{method:'POST',headers:{Host:'dealdeskdemo.duckdns.org',Origin:origin,Cookie:`dd_operator=${cookie}`,'Content-Type':'application/json','Content-Length':'512','X-CSRF-Token':body.csrf,'Idempotency-Key':'oversize-test'},body:'x'.repeat(600)}))).status).toBe(413);
    expect(vi.mocked(create)).not.toHaveBeenCalled();
    expect((await launch(post('B01/RC01'))).status).toBe(202);
    expect(vi.mocked(create)).toHaveBeenCalledOnce();
    expect((await passwordLogin(new NextRequest(origin+'/api/auth/login',{method:'POST'}))).status).toBe(404);
  });
  it('caps all anonymous sessions together while preserving a bounded idempotent retry', () => {
    const allow = createLaunchLimiter(); const now = 1_000_000;
    for (let i=0;i<8;i++) expect(allow(`session-${i}`,`key-${i}`,now)).toBe(true);
    expect(allow('new-session','new-key',now)).toBe(false);
    expect(allow('session-0','key-0',now)).toBe(true);
    expect(allow('new-session','new-key',now+60_001)).toBe(true);
    const perSession = createLaunchLimiter();
    for (let i=0;i<4;i++) expect(perSession('same-session',`key-${i}`,now)).toBe(true);
    expect(perSession('same-session','fifth-key',now)).toBe(false);
    expect(perSession('different-session','fifth-key',now)).toBe(true);
  });
});
