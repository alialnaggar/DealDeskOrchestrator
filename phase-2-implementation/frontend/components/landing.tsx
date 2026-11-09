'use client';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { csrf, Created, json } from './client';
import { ArchitectureDiagram } from './architecture-diagram';
import { z } from 'zod';

const scenarios = [
  { code: 'B01/RC01', title: 'Revised Deal', number: '01', detail: 'Review a delivery alternative and its required checks.', foot: '10 units requested by 04 Sep 2026; the checked alternative changes the delivery date. Customer acceptance remains pending.' },
  { code: 'N01/UC02', title: 'Missing Evidence', number: '02', detail: 'Explore how unresolved credit evidence affects a deal decision.', foot: 'Fixed Credit remains unknown. Stale or unavailable evidence prevents a verified candidate.' }
] as const;

export function Landing({ publicAccess = false }: { publicAccess?: boolean }) {
  const router = useRouter();
  const [auth, setAuth] = useState(false); const [token, setToken] = useState(''); const [password, setPassword] = useState(''); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const launching = useRef(false);
  useEffect(() => { csrf().then(r => { setAuth(r.authenticated); setToken(r.csrf); }).catch(() => setError('Demo session unavailable. Refresh to try again.')); }, []);
  async function login(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError('');
    try {
      await json('/api/auth/login', z.object({ authenticated: z.literal(true) }).strict(), { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token }, body: JSON.stringify({ password }) });
      setPassword(''); const r = await csrf(); setToken(r.csrf); setAuth(r.authenticated);
    } catch { setError('Login refused. Check operator credentials and local origin.'); } finally { setBusy(false); }
  }
  async function launch(scenario: string) {
    if (launching.current || !auth || !token) return;
    launching.current = true; setBusy(true); setError('');
    // Preserve the idempotency key after a lost response; never auto-replay a run.
    const storageKey = `dealdesk.pending.${scenario}`;
    const key = sessionStorage.getItem(storageKey) || crypto.randomUUID();
    sessionStorage.setItem(storageKey, key);
    try {
      const result = await json('/api/assessments', Created, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token, 'Idempotency-Key': key }, body: JSON.stringify({ scenario }) });
      sessionStorage.removeItem(storageKey);
      router.push(`/assessments/${result.assessment_id}`);
    } catch (e) {
      const code = e instanceof Error && 'status' in e ? e.status : 0;
      setError(code === 401 ? 'Session expired. Refresh the page; your launch key is retained for a safe retry.' : code === 429 ? 'Demo launch limit reached. Try again later; your launch key is retained.' : 'Launch unavailable. Retry will reuse the same request key, not start a second run.');
      if (code === 401) { setAuth(false); setToken(''); void csrf().then(r => { setAuth(r.authenticated); setToken(r.csrf); }); }
      setBusy(false); launching.current = false;
    }
  }
  return <main id="main-content" className="demo-home">
    <section className="home-intro" aria-labelledby="demo-title"><span className="eyebrow">DEAL DESK / SUPERVISOR DEMONSTRATION</span><h1 id="demo-title">Intelligent deal assessment.</h1><p>Six specialist responsibilities. One coordinated decision-support workflow.</p></section>
    <ArchitectureDiagram />
    <section className="scenario-section" aria-labelledby="choose"><div className="section-heading"><div><span className="eyebrow">OFFLINE-SCRIPTED DEMONSTRATION</span><h2 id="choose">Explore two synthetic scenarios</h2></div><span className="pill">Human review required</span></div>
      <div className="scenario-grid">{scenarios.map(s => <article className="scenario panel" key={s.code}><div className="scenario-top"><span className="scenario-num" aria-hidden="true">{s.number}</span><span className="scenario-code">{s.code}</span></div><span className="eyebrow">SCENARIO {s.number}</span><h3>{s.title}</h3><p>{s.detail}</p><div className="scenario-foot">{s.foot}</div><button type="button" aria-label={`Run ${s.code} offline assessment`} onClick={() => launch(s.code)} disabled={!auth || !token || busy}>Explore scenario <span aria-hidden="true">↗</span></button></article>)}</div>
      {publicAccess && !auth && !error ? <p role="status" className="session-note">Preparing your synthetic demo session…</p> : null}
    </section>
    {!publicAccess && !auth ? <section className="panel login" aria-label="Operator login"><div><span className="eyebrow">LOCAL OPERATOR SESSION</span><h2>Enter the demo workspace</h2><p>Sign in to launch one of the two allowlisted synthetic assessments.</p></div><form onSubmit={login}><label htmlFor="password">Operator password</label><input id="password" type="password" required minLength={32} autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} /><button disabled={busy || !token}>Enter workspace <span aria-hidden="true">→</span></button></form></section> : null}
    {error ? <p role="alert" className="error">{error}</p> : null}
  </main>;
}
