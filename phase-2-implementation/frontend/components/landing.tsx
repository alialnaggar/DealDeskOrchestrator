'use client';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { csrf, Created, json } from './client';
import { z } from 'zod';
const scenarios = [
  { code: 'B01/RC01', title: 'Delivery revision', icon: '01', kicker: 'SUPPORTED ALTERNATIVE', detail: '10 units requested by 04 Sep 2026. Only 8 available by the requested date.', foot: 'Verified offline candidate: 8 on 03 Sep + 2 on 08 Sep. Customer acceptance pending.' },
  { code: 'N01/UC02', title: 'Credit uncertainty', icon: '02', kicker: 'EVIDENCE GAP', detail: 'Fixed Credit is unknown because selected evidence is stale or incomplete.', foot: 'No verified candidate. A completed scripted AI stage is not credit clearance.' }
] as const;
export function Landing() {
  const router = useRouter(); const [auth, setAuth] = useState(false); const [token, setToken] = useState(''); const [password, setPassword] = useState(''); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const launching = useRef(false);
  useEffect(() => { csrf().then(r => { setAuth(r.authenticated); setToken(r.csrf); }).catch(() => setError('Operator session unavailable.')); }, []);
  async function login(e: React.FormEvent) { e.preventDefault(); setBusy(true); setError(''); try { await json('/api/auth/login', z.object({ authenticated: z.literal(true) }).strict(), { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token }, body: JSON.stringify({ password }) }); setPassword(''); const r = await csrf(); setToken(r.csrf); setAuth(r.authenticated); } catch { setError('Login refused. Check operator credentials and local origin.'); } finally { setBusy(false); } }
  async function launch(scenario: string) {
    if (launching.current || !auth || !token) return;
    launching.current = true; setBusy(true); setError('');
    // Keep the key across a lost response and a browser refresh. A retry must not
    // schedule another assessment when the first POST already committed.
    const storageKey = `dealdesk.pending.${scenario}`;
    const key = sessionStorage.getItem(storageKey) || crypto.randomUUID();
    sessionStorage.setItem(storageKey, key);
    try {
      const result = await json('/api/assessments', Created, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token, 'Idempotency-Key': key }, body: JSON.stringify({ scenario }) });
      sessionStorage.removeItem(storageKey);
      router.push(`/assessments/${result.assessment_id}`);
    } catch (e) {
      setError(e instanceof Error && 'status' in e && e.status === 401 ? 'Operator session expired. Sign in again; your launch key is retained for a safe retry.' : 'Launch unavailable. Retry will reuse the same request key, not start a second run.');
      if (e instanceof Error && 'status' in e && e.status === 401) { setAuth(false); setToken(''); void csrf().then(r => setToken(r.csrf)); }
      setBusy(false); launching.current = false;
    }
  }
  return <main><section className="hero"><div className="eyebrow">DECISION INTELLIGENCE / OFFLINE DEMONSTRATION</div><h1>Clarity before<br/><em>commitment.</em></h1><p>Watch six original-subject specialist stages, inspect deterministic checks and compare a source-grounded delivery revision. The final decision stays with a person.</p><div className="hero-note">SYNTHETIC FIXTURE PREVIEW · Not live business records, hosted model inference or an approval system</div></section>
    {!auth ? <section className="panel login" aria-label="Operator login"><div><span className="eyebrow">RESTRICTED WORKSPACE</span><h2>Operator access</h2><p>Local-only, time-limited session. Credentials are not sent to Python from the browser.</p></div><form onSubmit={login}><label htmlFor="password">Operator password</label><input id="password" type="password" required minLength={32} autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} /><button disabled={busy || !token}>Enter workspace →</button></form></section> : <section aria-labelledby="choose"><div className="section-heading"><div><span className="eyebrow">01 / ASSESSMENT LAUNCH</span><h2 id="choose">Choose a synthetic scenario</h2></div><span className="pill">2 authorized fixtures</span></div><div className="scenario-grid">{scenarios.map(s => <article className="scenario panel" key={s.code}><span className="scenario-num">{s.icon}</span><span className="eyebrow">{s.kicker} · {s.code}</span><h3>{s.title}</h3><p>{s.detail}</p><div className="scenario-foot">{s.foot}</div><button aria-label={`Run ${s.code} offline assessment`} onClick={() => launch(s.code)} disabled={busy}>Run genuine offline assessment <span aria-hidden>↗</span></button></article>)}</div></section>}
    {error && <p role="alert" className="error">{error}</p>}<section className="method"><span className="eyebrow">METHOD / AUTHORITY</span><p>LangGraph checkpoints and PostgreSQL event ordering drive this display. Offline-scripted observations are distinct from fixed Python decisions; candidates never reserve, approve or accept a deal.</p></section></main>;
}
