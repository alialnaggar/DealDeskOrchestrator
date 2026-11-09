'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { type EventDTO, type ReviewDTO, type StatusDTO, specialists } from '@/lib/contracts';
import { ApiError, events, matchStatus, review, status } from './client';
import { assessmentLabel, assessmentTone, findingTone, stageLabel } from '@/lib/presentation';
import { DealRecord } from './deal-record';
import { guideForCode } from '@/lib/scenario-guide';

const names: Record<string, string> = { configuration: 'Configuration', pricing: 'Pricing & margin', fulfillment: 'Fulfillment', credit: 'Credit & risk', policy: 'Policy & compliance', approval_routing: 'Approval routing' };
const label = (value: string) => value.replaceAll('_', ' ');
const stamp = (value: string) => new Date(value).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'medium', timeZone: 'UTC' }) + ' UTC';
const day = (value: string) => new Date(`${value}T12:00:00Z`).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
export function DecisionBrief({ data }: { data: ReviewDTO }) {
  const c = data.candidate_comparison;
  const lines = data.original.lines;
  const later = c?.proposed_slices.some(slice => slice.delivery_date > c.original_requested_date);
  return <section className="panel decision-brief" aria-labelledby="brief-heading">
    <span className="eyebrow">01 / CUSTOMER REQUEST AND DECISION</span>
    <h2 id="brief-heading">{c ? later ? 'A later delivery needs the customer’s decision' : 'The proposed schedule needs customer review' : data.original.specialists.credit.fixed_finding === 'unknown' ? 'Evidence is insufficient for a verified alternative' : 'No verified alternative was produced'}</h2>
    <p className="brief-intro">The assessment is complete, but the original deal remains <strong>{label(data.original.business_status)}</strong>. Completion means the checks ran; it does not mean the deal is cleared.</p>
    <div className="brief-grid">
      <div><span className="eyebrow">ORIGINAL REQUEST · V0</span><strong>{lines.map(l => `${l.quantity} units`).join(' · ')}</strong><p>Requested by {day(data.original.requested_delivery_date)}. {data.original.availability.map(a => `${a.quantity_by_requested_date} of ${a.requested_quantity} units supported by that date`).join('; ') || 'Availability not reported'}.</p></div>
      <div><span className="eyebrow">WHY IT CANNOT PROCEED UNCHANGED</span><strong>{data.original.specialists.credit.fixed_finding === 'unknown' ? 'Credit remains unknown' : data.original.revision_reasons.some(r => r.code === 'requested_date_not_supported') ? 'Original delivery date not supported' : data.original.revision_reasons.length ? data.original.revision_reasons.map(r => label(r.code)).join(' · ') : 'Review required'}</strong><p>{data.original.specialists.credit.fixed_finding === 'unknown' ? `Fixed Credit is unknown; ${data.original.specialists.credit.evidence_gaps.length ? `${data.original.specialists.credit.evidence_gaps.map(g => label(g.reason_code)).join(' and ')} evidence needs human review` : 'the unknown finding needs human review'}.` : c ? later ? 'The proposed schedule changes the customer’s requested date.' : 'The alternative still requires human review.' : 'No verified candidate was produced.'}</p></div>
      <div><span className="eyebrow">VERIFIED ALTERNATIVE · V1</span><strong>{c ? c.proposed_slices.map(s => `${s.quantity} on ${day(s.delivery_date)}`).join(' + ') : 'None verified'}</strong><p>{c ? `Deterministic checks: ${label(c.fixed_supply_status)}; ${label(c.reservation_status)}. Customer acceptance: ${c.customer_acceptance}.` : 'A completed scripted stage is not a credit decision or a delivery proposal.'}</p></div>
    </div>
    <p className="brief-boundary"><strong>Human handoff:</strong> {c ? 'Request customer acceptance of the changed date and human review.' : 'Request missing or current evidence and human review.'} {data.original.routing_roles_status === 'unavailable_while_route_withheld' ? 'Routing is withheld.' : `Routing status: ${label(data.original.routing_roles_status)}.`} {c && 'No stock is reserved.'} No approval is granted here.</p>
  </section>;
}
export function SpecialistMatrix({ data, rows, scenario }: { data: ReviewDTO | null; rows: EventDTO[]; scenario?: string }) {
  return <section className="panel specialist-panel" aria-labelledby="specialists"><div className="section-heading"><div><span className="eyebrow">02 / ORIGINAL SUBJECT · V0</span><h2 id="specialists">Six specialist responsibilities</h2></div><span className="pill">Two kinds of evidence</span></div><p className="section-guide">The left column reports fixed checks. The right reports original-subject offline-scripted execution, citations and gaps. A completed stage does not mean the deal passed.</p><div className="matrix-head" aria-hidden="true"><span>SPECIALIST</span><span>DETERMINISTIC CHECK · ORIGINAL</span><span>OFFLINE-SCRIPTED STAGE · ORIGINAL</span></div>{specialists.map((name, i) => {
    const fixed = rows.some(e => e.kind === 'fixed_completed' && e.stage === name);
    const ai = rows.some(e => e.kind === 'ai_completed' && e.stage === name);
    const finding = data?.original.specialists[name];
    // Review is returned only after completion; do not display a projected
    // finding before the persisted event for that particular stage is replayed.
    const fixedFinding = fixed ? finding : null;
    const scriptedFinding = ai ? finding : null;
    return <div className="matrix-row" key={name}><div className="matrix-name"><span className="index">0{i+1}</span><strong>{names[name]}</strong></div><div className="matrix-cell"><span className="mobile-column">DETERMINISTIC CHECK</span><span className={`status ${fixed ? 'checked' : 'muted'}`}>{fixed ? 'Check ran' : 'Pending'}</span>{fixedFinding && <p className={`finding-text ${findingTone(fixedFinding.fixed_finding)}`}>{label(fixedFinding.fixed_finding)}</p>}{fixedFinding && fixedFinding.fixed_rule_ids.length > 0 && <small>Rules: {fixedFinding.fixed_rule_ids.join(', ')}</small>}</div><div className="matrix-cell"><span className="mobile-column">OFFLINE-SCRIPTED STAGE</span><span className={`status ${scriptedFinding?.ai_original_execution === 'abstained' ? 'warning' : ai ? 'checked' : 'muted'}`}>{scriptedFinding ? label(scriptedFinding.ai_original_execution || 'not available') : ai ? 'Checkpointed · outcome pending review' : 'Pending'}</span>{scriptedFinding && scriptedFinding.ai_original_citations.length > 0 && <small>Validated refs: {scriptedFinding.ai_original_citations.map((c,i) => <span key={`${c.ref}-${c.field}`}>{i > 0 ? ", " : ""}{scenario ? <Link href={`/scenarios/${scenario === "B01/RC01" ? "rc01" : "uc02"}#deal-record`}>{c.ref} ({c.field})</Link> : `${c.ref} (${c.field})`}</span>)}</small>}{scriptedFinding && scriptedFinding.evidence_gaps.length > 0 && <small className="gap-note">Missing information: {scriptedFinding.evidence_gaps.map(g => `${label(g.reason_code)} · ${label(g.requirement_id)}`).join('; ')}</small>}</div></div>;
  })}<p className="footnote">“Completed” events confirm checkpointed execution, not a positive finding. Abstentions and evidence gaps appear only in the validated review. The candidate, if present, receives six fixed checks—not six AI reruns.</p></section>;
}
export function EvidenceReview({ data }: { data: ReviewDTO }) {
  const gaps = specialists.flatMap(name => data.original.specialists[name].evidence_gaps.map(gap => ({ name, gap })));
  const rules = specialists.flatMap(name => data.original.specialists[name].fixed_rule_ids.map(rule => ({ name, rule })));
  return <section className="panel evidence-panel" aria-labelledby="evidence-heading">
    <div className="section-heading"><div><span className="eyebrow">03 / EVIDENCE &amp; RULES</span><h2 id="evidence-heading">What the source supports</h2></div><span className="pill">Original request</span></div>
    <p className="section-guide">Only validated references returned by this review are shown. No listed gap does not imply clearance.</p>
    <div className="evidence-grid"><div><h3>Missing or uncertain evidence</h3>{gaps.length ? <ul>{gaps.map(({name,gap},i) => <li key={`${name}-${i}`}><strong>{names[name]} · {label(gap.reason_code)}</strong><span>{label(gap.requirement_id)} · next: {label(gap.next_action_code)}</span></li>)}</ul> : <p>No specialist gap entries returned for the original. Inspect the fixed findings before taking action.</p>}</div>
      <div><h3>Fixed rule references</h3>{rules.length ? <ul>{rules.map(({name,rule},i) => <li key={`${name}-${i}`}><strong>{names[name]}</strong><span>{rule}</span></li>)}</ul> : <p>No fixed rule identifiers returned for the original.</p>}{data.original.blockers.length > 0 ? <p className="evidence-callout">Blocking findings: {data.original.blockers.map(b => label(b.code)).join(' · ')}. No override is available here.</p> : null}</div></div>
  </section>;
}
export function Comparison({ data }: { data: ReviewDTO }) {
  const c = data.candidate_comparison; const candidate = data.candidate;
  if (!c || !candidate) return <section className="panel" aria-labelledby="comparison"><span className="eyebrow">LOOP 2 · CANDIDATE EVALUATION</span><h2 id="comparison">No verified candidate</h2><p>No alternative was verified for this assessment. Fixed Credit is {label(data.original.specialists.credit.fixed_finding)}; {data.original.specialists.credit.ai_original_execution === 'completed' ? 'a completed offline-scripted observation is not clearance' : data.original.specialists.credit.ai_original_execution === 'abstained' ? 'the offline-scripted Credit observation abstained' : 'no offline-scripted Credit outcome is available'}.</p><p>Evidence gaps: {data.original.specialists.credit.evidence_gaps.map(g => label(g.reason_code)).join(', ') || 'none reported'}.</p></section>;
  return <section className="panel" aria-labelledby="comparison"><span className="eyebrow">LOOP 2 — REVISED CANDIDATE EVALUATION</span><h2 id="comparison">Original Deal | Revised Candidate</h2><p>One offline-scripted Fulfillment proposal, citing source inventory and inbound supply. V1 has six deterministic checks—not six candidate AI executions or a full specialist rerun.</p><div className="compare-grid"><div className="compare-card original"><span className="eyebrow">V0 / ORIGINAL REQUEST</span><strong>{c.original_quantity} units</strong><span>by {day(c.original_requested_date)}</span><div className="bar"><span style={{width:'100%'}} /></div><small>Available by requested date: {data.original.availability.find(a => a.line_id === c.original_line_id)?.quantity_by_requested_date ?? 'unknown'} / {c.original_quantity}</small></div><div className="compare-card revised"><span className="eyebrow">V1 / CHECKED ALTERNATIVE</span><div className="slices">{c.proposed_slices.map((slice,i) => <div key={i}><strong>{slice.quantity}</strong><span> units · {day(slice.delivery_date)}</span><div className="bar"><span style={{width:`${Math.min(100, slice.quantity/c.original_quantity*100)}%`}} /></div><small>Source refs: {slice.source_refs.join(', ') || 'none returned'}</small></div>)}</div></div></div><div className="facts"><span className="status warning">{label(c.fixed_supply_status)}</span><span className="status warning">{label(candidate.business_status)}</span><span className="status warning">Customer acceptance: {c.customer_acceptance}</span><span className="status warning">{label(c.reservation_status)}</span></div><p>Remaining customer constraint: {c.unmet_customer_constraints.map(label).join(', ')}. Routing: {label(candidate.routing_roles_status)}; required roles {candidate.required_roles === null ? 'unavailable while withheld' : candidate.required_roles.length ? candidate.required_roles.map(r => r.role).join(', ') : 'none returned by the fixed interface'}.</p><div className="checks"><h3>Candidate deterministic checks · V1 only</h3><div className="checks-grid">{specialists.map(name => <div key={name}><span>{names[name]}</span><strong>{label(candidate.specialists[name].fixed_finding)}</strong><small>{candidate.specialists[name].fixed_rule_ids.join(', ') || 'No rule hits returned'}</small></div>)}</div></div></section>;
}
export function HumanReview({ data }: { data: ReviewDTO }) { return <section className="panel" aria-labelledby="human"><span className="eyebrow">05 / HUMAN AUTHORITY</span><h2 id="human">Review, not authorization</h2><div className="authority"><strong>{label(data.authorization)}</strong><p>Routing is {label(data.original.routing_roles_status)}. Required roles: {data.original.required_roles === null ? 'unavailable while routing is withheld' : data.original.required_roles.length === 0 ? 'none returned by the fixed interface' : data.original.required_roles.map(r => r.role).join(', ')}. No approval, reservation or customer acceptance can be performed here.</p></div><h3>Source-grounded recommendations</h3><div className="recommendations">{data.recommendations.map((r,i) => <div key={i}><span className="eyebrow">{names[r.specialist]} · {label(r.verification)}</span><strong>{label(r.action_code)}</strong><small>Subject {r.subject_id} {r.rule_ids.length ? `· rules ${r.rule_ids.join(', ')}` : ''} {r.source_refs.length ? `· sources ${r.source_refs.join(', ')}` : ''}</small></div>)}</div><p className="footnote">Permitted next steps (outside this UI): {data.permitted_next_actions.map(label).join(' · ')}.</p></section>; }
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
        <div className="summary"><div><span>BUSINESS OUTCOME</span><strong>{label(visibleReview.original.business_status)}</strong></div><div><span>EVENTS RECORDED</span><strong>{state.last_sequence}</strong></div><div><span>CANDIDATE</span><strong>{visibleReview.candidate ? '1 · deterministic checks' : 'None verified'}</strong></div><div><span>AUTHORITY</span><strong>Human only</strong></div></div>
        <DecisionBrief data={visibleReview}/><EvidenceReview data={visibleReview}/>
        {guide && visibleReview.candidate && <DealRecord scenario={state.scenario === 'B01/RC01' ? 'rc01' : 'uc02'} candidate={visibleReview}/>}
        <Comparison data={visibleReview}/><HumanReview data={visibleReview}/>
      </>}
      <details className="panel trace-details"><summary>Inspect technical trace · {shown.length} persisted events</summary><Timeline rows={shown} data={visibleReview} state={state}/></details>
    </>}
  </main>;
}
