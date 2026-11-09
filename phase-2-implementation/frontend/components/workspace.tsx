'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { type EventDTO, type ReviewDTO, type StatusDTO } from '@/lib/contracts';
import { ApiError, events, matchStatus, review, status } from './client';
import { assessmentLabel, assessmentTone, stageLabel } from '@/lib/presentation';
import { DealRecord } from './deal-record';
import { guideForCode } from '@/lib/scenario-guide';

const label = (value: string) => value.replaceAll('_', ' ');
const stamp = (value: string) => new Date(value).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'medium', timeZone: 'UTC' }) + ' UTC';
const day = (value: string) => new Date(`${value}T12:00:00Z`).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
const units = (value: string) => /^\d+(?:\.\d+)?$/.test(value) ? Number(value).toLocaleString('en-GB') : value;
export function DecisionBrief({ data }: { data: ReviewDTO }) {
  const c = data.candidate_comparison;
  const lines = data.original.lines;
  const later = c?.proposed_slices.some(slice => slice.delivery_date > c.original_requested_date);
  const stale = data.original.specialists.credit.evidence_gaps.some(g => g.requirement_id === 'credit_commitments_fresh' && g.reason_code === 'stale' && g.verification === 'verified');
  return <section className="panel decision-brief" aria-labelledby="brief-heading">
    <span className="eyebrow">01 / CUSTOMER REQUEST AND DECISION</span>
    <h2 id="brief-heading">{c ? later ? 'A later delivery needs the customer’s decision' : 'The proposed schedule needs customer review' : data.original.specialists.credit.fixed_finding === 'unknown' ? 'Evidence is insufficient for a verified alternative' : 'No verified alternative was produced'}</h2>
    <p className="brief-intro">The assessment is complete, but the original deal remains <strong>{label(data.original.business_status)}</strong>. Completion means the checks ran; it does not mean the deal is cleared.</p>
    <div className="brief-grid">
      <div><span className="eyebrow">ORIGINAL REQUEST · V0</span><strong>{lines.map(l => `${l.quantity} units`).join(' · ')}</strong><p>Requested by {day(data.original.requested_delivery_date)}. {data.original.availability.map(a => `${units(a.quantity_by_requested_date)} of ${a.requested_quantity} units supported by that date`).join('; ') || 'Availability not reported'}.</p></div>
      <div><span className="eyebrow">WHY IT CANNOT PROCEED UNCHANGED</span><strong>{data.original.revision_reasons.some(r => r.code === 'requested_date_not_supported') ? 'Original delivery date not supported' : 'Human review required'}</strong><p>{data.original.specialists.credit.fixed_finding === 'unknown' ? `Credit remains unresolved${stale ? ': the recorded commitments are stale' : ''}. This is not a failed credit check.` : c && later ? 'The checked alternative moves part of delivery beyond the requested date.' : 'The original request still requires human review.'}</p></div>
      <div><span className="eyebrow">CHECKED ALTERNATIVE · V1</span><strong>{c ? c.proposed_slices.map(s => `${s.quantity} on ${day(s.delivery_date)}`).join(' + ') : 'None verified'}</strong><p>{c ? 'Rule-based checks support the proposed supply, but no stock is reserved. Customer acceptance is pending; this is not an approved order.' : 'No verified alternative was returned. A recorded specialist observation alone is not credit clearance or a delivery proposal.'}</p></div>
    </div>
    <p className="brief-boundary"><strong>Human handoff:</strong> {c ? 'Request customer acceptance of the changed date and human review.' : `${stale ? 'Request current credit commitments; ' : ''}${data.original.revision_reasons.some(r => r.code === 'requested_date_not_supported') ? 'investigate delivery with a human; ' : ''}request human review.`} {data.original.routing_roles_status === 'unavailable_while_route_withheld' ? 'Approval routing is withheld; no eligible approver is identified by this review.' : 'Inspect the approval roles returned by the review.'} {c && 'No stock is reserved.'} No approval is granted here.</p>
  </section>;
}
export { SpecialistMatrix, EvidenceReview } from './business-findings';
import { SpecialistMatrix, EvidenceReview } from './business-findings';
export { Comparison, HumanReview } from './decision-tail';
import { Comparison, HumanReview } from './decision-tail';
export function Timeline({ rows, data, state }: { rows: EventDTO[]; data: ReviewDTO | null; state: StatusDTO | null }) { return <section className="panel" aria-labelledby="trace"><span className="eyebrow">06 / TECHNICAL INSPECTION</span><h2 id="trace">Durable execution trace</h2><p>LangGraph checkpoints · PostgreSQL append-only events · original-only scripted observations · deterministic candidate verification</p><dl className="provenance"><div><dt>Assessment</dt><dd>{state?.assessment_id}</dd></div><div><dt>Execution mode</dt><dd>{state?.mode}</dd></div><div><dt>Phase 1C pin</dt><dd>{state?.phase1c_pin}</dd></div>{data && <><div><dt>Run ID</dt><dd>{data.phase1c_run_id}</dd></div><div><dt>Source input digest</dt><dd>{data.source_input_digest}</dd></div><div><dt>Sealed bundle digest</dt><dd>{data.bundle_sha256}</dd></div><div><dt>Candidate input digest</dt><dd>{data.candidate_comparison?.candidate_input_digest || 'No verified candidate'}</dd></div><div><dt>Candidate fixed supply</dt><dd>{data.candidate_comparison?.fixed_supply_status || 'Not applicable'}</dd></div><div><dt>Authorization gate</dt><dd>{data.authorization}</dd></div></>}</dl><ol className="timeline" tabIndex={0} aria-label="Ordered assessment events">{rows.map(e => <li key={e.sequence}><span className="seq">{String(e.sequence).padStart(2,'0')}</span><span><strong>{stageLabel[e.kind]}</strong> {e.stage && <small> / {label(e.stage)}</small>}</span><time dateTime={e.occurred_at}>{stamp(e.occurred_at)}</time></li>)}</ol><p className="footnote">Timestamps are stored API observations. No raw checkpoint, provider receipt, model prose or sensitive credit record is exposed.</p></section>; }
export function Workspace({ id }: { id: string }) {
  const [state, setState] = useState<StatusDTO | null>(null); const [rows, setRows] = useState<EventDTO[]>([]); const [data, setData] = useState<ReviewDTO | null>(null); const [error, setError] = useState(''); const [needsLogin, setNeedsLogin] = useState(false); const [loading, setLoading] = useState(true); const [replayed, setReplayed] = useState(0);
  const cursor = useRef<EventDTO[]>([]); const inFlight = useRef(false);
  const refresh = useCallback(async () => {
    if (inFlight.current) return; inFlight.current = true;
    try {
      let s = matchStatus(await status(id), id);
      const page = await events(id, cursor.current.length);
      const complete = [...cursor.current, ...page];
      if (page.some((e,i) => e.sequence !== cursor.current.length+i+1)) throw new Error('Persisted event sequence incomplete; retrying');
      if (complete.length > s.last_sequence) s = matchStatus(await status(id), id);
      if (complete.length !== s.last_sequence) throw new Error('Persisted event history incomplete; retrying');
      let r: ReviewDTO | null = null;
      if (s.status === 'completed') {
        r = await review(id);
        if (r.assessment_id !== id || r.phase1c_pin !== s.phase1c_pin) throw new Error('Review identity mismatch');
      }
      cursor.current = complete; setState(s); setRows(complete); setData(r);
      setError(''); setNeedsLogin(false); setLoading(false);
    } catch(e) {
      // Do not leave a previously completed outcome visible after logout, source
      // drift or a lost backend. The cursor stays local for a safe incremental retry.
      setState(null); setRows([]); setData(null); setReplayed(0); setLoading(false);
      const code = e instanceof ApiError ? e.status : 0;
      setNeedsLogin(code === 401);
      setError(code === 401 ? 'Operator session expired. Return to the homepage to refresh your demo session.'
        : code === 403 ? 'Access refused. Check the local operator session.'
        : code === 404 ? 'Assessment not found or unavailable to this operator.'
        : code === 409 ? 'Source evidence changed or review is unavailable. Display withheld; inspect the offline API.'
        : code === 502 || code === 503 ? 'Local offline service unavailable or its response changed. Retrying; review withheld.'
        : 'Assessment response inconsistent or temporarily unavailable. Retrying; review withheld.');
    } finally { inFlight.current = false; }
  }, [id]);
  useEffect(() => { let active = true; const run = () => { if (active) void refresh(); }; run(); const timer = setInterval(run, 2500); return () => { active = false; clearInterval(timer); }; }, [refresh]);
  useEffect(() => { if (!rows.length || error || replayed >= rows.length) return; const timer = setTimeout(() => setReplayed(n => n+1), 320); return () => clearTimeout(timer); }, [rows, error, replayed]);
  const shown = rows.slice(0,replayed);
  const ready = shown.some(e => e.kind === 'review_ready');
  const visibleReview = ready ? data : null;
  const guide = state && guideForCode(state.scenario);
  return <main id="main-content" className="workspace guided"><div className="back"><Link href="/#scenarios">← Explore scenarios</Link><span> / ASSESSMENT WORKSPACE</span></div>
    <section className="workspace-hero"><div><span className="eyebrow">PERSISTED EVENT REPLAY · OFFLINE SCRIPTED</span><h1>{guide?.title || 'Assessment workspace'}</h1><p>Assessment <code>{id}</code> · Recorded milestones, not live model streaming</p></div><span aria-live="polite" className={`large-status tone-${state ? assessmentTone[state.status] : error ? 'caution' : 'info'}`}>{error ? 'Review withheld' : !state ? 'Loading' : state.status === 'completed' && !ready ? 'Replaying persisted events' : assessmentLabel[state.status]}</span></section>
    {loading && <div role="status" className="panel">Loading persisted status and events…</div>}
    {error && <div className="error panel" role="alert">{error} {needsLogin ? <Link href="/">Return to homepage</Link> : <button type="button" className="retry" onClick={() => void refresh()}>Retry now</button>}</div>}
    {state && <>
      <section className="panel replay-panel" aria-labelledby="replay-title"><span className="eyebrow">ACTUAL PERSISTED SEQUENCE</span><h2 id="replay-title">Assessment timeline</h2><p className="section-guide">Replaying recorded boundaries in order. Completed events indicate checkpointed work, not favorable findings; projected review data appears only when its supporting stage has been shown.</p><progress max={Math.max(rows.length,1)} value={shown.length} aria-label="Recorded milestones replayed"/><p aria-live="polite">{shown.length} of {rows.length} recorded milestones shown</p><ol className="replay-list">{shown.map(e => <li key={e.sequence}><span className="seq">{String(e.sequence).padStart(2,'0')}</span><strong>{stageLabel[e.kind]}</strong> <span>{e.stage && `· ${label(e.stage)}`}</span></li>)}</ol></section>
      {(state.status === 'stopped' || state.status === 'uncertain') && <div role="alert" className="panel warning-box">Execution {state.status}. No automatic replay; request a new assessment only after human inspection.</div>}
      <SpecialistMatrix data={data} rows={shown} scenario={state.scenario}/>
      {visibleReview && <>
        <div className="summary"><div><span>BUSINESS OUTCOME</span><strong>{label(visibleReview.original.business_status)}</strong></div><div><span>EVENTS RECORDED</span><strong>{state.last_sequence}</strong></div><div><span>CANDIDATE</span><strong>{visibleReview.candidate ? '1 · checked proposal' : 'None verified'}</strong></div><div><span>AUTHORITY</span><strong>Human only</strong></div></div>
        <DecisionBrief data={visibleReview}/><EvidenceReview data={visibleReview}/>
        {guide && visibleReview.candidate && <DealRecord scenario={state.scenario === 'B01/RC01' ? 'rc01' : 'uc02'} candidate={visibleReview}/>}
        <Comparison data={visibleReview}/><HumanReview data={visibleReview}/>
      </>}
      <details className="panel trace-details"><summary>Inspect technical trace · {shown.length} persisted events</summary><Timeline rows={shown} data={visibleReview} state={state}/></details>
    </>}
  </main>;
}
