'use client';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { z } from 'zod';
import { csrf, Created, json } from './client';
import { DealRecord, ResponsibilityFlow } from './deal-record';
import { guides, type GuideKey } from '@/lib/scenario-guide';

export function ScenarioIntro({scenario, guide, publicAccess, intake=null}: {scenario: GuideKey; guide: typeof guides[GuideKey]; publicAccess: boolean;intake?:{digest:string;receipt:string}|null}) {
  const router = useRouter(); const launching = useRef(false);
  const [token,setToken] = useState(''); const [auth,setAuth] = useState(false);
  const [password,setPassword] = useState(''); const [busy,setBusy] = useState(false); const [error,setError] = useState('');
  useEffect(() => { void csrf().then(r => {setToken(r.csrf);setAuth(r.authenticated);}).catch(() => setError('Session unavailable. Refresh to try again.')); }, []);
  async function run() {
    if (!auth || !token || launching.current) return;
    launching.current = true; setBusy(true); setError('');
    const storageKey = `dealdesk.pending.${guide.code}`;
    const key = sessionStorage.getItem(storageKey) || crypto.randomUUID();
    sessionStorage.setItem(storageKey,key);
    try {
      const result = await json('/api/assessments', Created, {method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':token,'Idempotency-Key':key},body:JSON.stringify({scenario:guide.code})});
      sessionStorage.removeItem(storageKey);
      router.push(`/assessments/${result.assessment_id}${intake?`?intake=${encodeURIComponent(intake.receipt)}`:''}`);
    } catch (e) {
      const code = e instanceof Error && 'status' in e ? e.status : 0;
      setError(code === 429 ? 'Launch limit reached. Retry later with the same saved key.' : 'Launch unavailable. Retry will reuse the saved request key, not start a second run.');
      if (code === 401) void csrf().then(r => {setToken(r.csrf);setAuth(r.authenticated);});
      launching.current = false; setBusy(false);
    }
  }
  return <main id="main-content" className="workspace guided"><div className="back"><Link href="/#scenarios">← Explore scenarios</Link> / PRE-RUN BRIEF</div>
    <section className="workspace-hero"><div><span className="eyebrow">{guide.code} · SYNTHETIC SOURCE PREVIEW</span><h1>{guide.title}</h1><p>{guide.description}</p></div><span className="large-status tone-info">Focus: {guide.focus}</span></section>
    {intake && <section className="panel intake-match" aria-label="Confirmed manual intake"><span className="eyebrow">MANUAL INTAKE · SERVER-VALIDATED MATCH</span><h2>Confirmed input matches this synthetic fixture</h2><p>Your reviewed commercial input matches the full supported {guide.code} request. This is a comparison, not a new deal record: the assessment runs the unchanged pinned fixture and retrieves its own specialist evidence. No entered deal data was persisted.</p><small>Confirmed input fingerprint: {intake.digest.slice(0,16)}… · <Link href="/intake">Start a different entry</Link></small></section>}
    <nav className="journey" aria-label="Demonstration journey"><a href="#deal-brief">Understand deal</a><a href="#deal-record">Inspect record</a><a href="#flow-title">Meet specialists</a><a href="#run-assessment">Run assessment</a></nav>
    <section id="deal-brief" className="panel"><span className="eyebrow">01 / BEFORE EXECUTION</span><h2>Deal brief</h2><div className="brief-grid"><div><strong>Customer request</strong><p>{guide.quantity} units of {guide.product}, requested by 04 Sep 2026 for Berlin. Quoted at €900 per unit, 30-day payment terms.</p></div><div><strong>What this tests</strong><p>{guide.objective}</p></div><div><strong>Constraint & risk</strong><p>{guide.risk}</p></div></div><p className="footnote">Expected behavior is a validation objective, not a prediction of a completed decision. All values in this preview are pinned synthetic fixture definitions, not a current database query.</p></section>
    <DealRecord scenario={scenario}/><ResponsibilityFlow focus={guide.focus}/>
    <section id="run-assessment" className="panel run-panel"><span className="eyebrow">02 / EXECUTE OFFLINE SYNTHETIC FIXTURE</span><h2>Ready to inspect the assessment?</h2><p>The service will run the allowlisted fixture and record ordered events. The next screen replays persisted milestones; no live AI stream or approval is offered.</p>
      <button type="button" className="run-button" disabled={!auth || !token || busy} onClick={() => void run()}>{busy ? 'Launching…' : 'Run Assessment'} <span aria-hidden="true">→</span></button>
      {!auth && !error && <p role="status">Preparing demo session…</p>}
      {!publicAccess && !auth && <form onSubmit={async e => {e.preventDefault();setBusy(true);try {await json('/api/auth/login',z.object({authenticated:z.literal(true)}).strict(),{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':token},body:JSON.stringify({password})});const r=await csrf();setToken(r.csrf);setAuth(r.authenticated);setError('');} catch {setError('Local login refused.');} finally {setBusy(false);}}}><label htmlFor="local-password">Local operator password</label><input id="local-password" type="password" value={password} onChange={e=>setPassword(e.target.value)}/><button type="submit">Enter local workspace</button></form>}
      {error && <p role="alert" className="error">{error}</p>}
    </section>
  </main>;
}
