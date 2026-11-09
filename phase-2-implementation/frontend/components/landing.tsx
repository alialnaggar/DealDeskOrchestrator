import Link from 'next/link';
import { ArchitectureDiagram } from './architecture-diagram';
import { guides } from '@/lib/scenario-guide';

const capabilities = [
  ['Governed orchestration', 'Pinned source context, checkpointed work and typed review; offline-scripted in this public demo.'],
  ['Separated responsibilities', 'Six fixed original checks; distinct scripted original-subject inspections. Not six live AI calls.'],
  ['Grounded evidence', 'Validated source citations, provenance and explicit gaps; no raw credit records exposed.'],
  ['Candidate discipline', 'One optional Fulfillment proposal must pass source and admissibility checks before six fixed candidate checks.'],
  ['Policy & uncertainty', 'Rule references, withheld routes and unknown findings are preserved rather than overridden.'],
  ['Human boundary & trace', 'Ordered persisted events lead to recommendations, not automatic approval or reservation.']
] as const;
const validation = [
  ['Typed contracts', 'Strict input/output DTOs and subject lineage'],
  ['Fixed rules', 'Phase 1C deterministic original and candidate verification'],
  ['Provenance', 'Pinned digest, citation binding and source-drift checks'],
  ['Admissibility', 'Proposal identity, slices and source references verified'],
  ['State & authority', 'Checkpoint/sequence validation; human-only approval gate']
] as const;

export function Landing({ publicAccess = false }: { publicAccess?: boolean }) {
  return <main id="main-content" className="demo-home">
    <section className="home-intro" aria-labelledby="demo-title"><span className="eyebrow">DEAL DESK / SOURCE-GROUNDED WORKFLOW</span><h1 id="demo-title">From request to responsible decision.</h1><p>Six specialist responsibilities. One coordinated decision-support workflow.</p></section>
    <ArchitectureDiagram />
    <section className="capabilities" aria-labelledby="capabilities-title"><div className="section-heading"><div><span className="eyebrow">WHAT THE IMPLEMENTATION DOES</span><h2 id="capabilities-title">System Capabilities &amp; Validation</h2></div></div><div className="capability-grid">{capabilities.map(([title,body],i) => <article className="panel" key={title}><span className="index">0{i+1}</span><h3>{title}</h3><p>{body}</p></article>)}</div><div className="validation panel"><h3>Validation techniques</h3><ul>{validation.map(([title,body]) => <li key={title}><strong>{title}</strong><span>{body}</span></li>)}</ul><p className="footnote">Architecture is broader than this two-scenario, offline-scripted execution. No hosted inference, automated approval, reservation or general deal entry is demonstrated.</p></div></section>
    <section id="scenarios" className="scenario-section" aria-labelledby="choose"><div className="section-heading"><div><span className="eyebrow">TWO SYNTHETIC CASES</span><h2 id="choose">Explore Scenarios</h2></div></div><div className="scenario-grid">{(Object.entries(guides) as [keyof typeof guides,typeof guides[keyof typeof guides]][]).map(([key,g],i) => <article className="scenario panel" key={key}><div className="scenario-top"><span className="scenario-num" aria-hidden="true">0{i+1}</span><span className="scenario-code">{g.code}</span></div><span className="eyebrow">SCENARIO 0{i+1}</span><h3>{g.title}</h3><p>{g.description}</p><p className="scenario-focus">Primary focus: <strong>{g.focus}</strong></p><ul className="traits">{g.traits.map(t => <li key={t}>{t}</li>)}</ul><Link className="scenario-action" aria-label={`Explore Scenario ${g.code}`} href={`/scenarios/${key}`}>Explore Scenario <span aria-hidden="true">↗</span></Link></article>)}</div>
      {!publicAccess && <p className="session-note">Local mode requires an operator session before running an assessment; the public synthetic demo does not.</p>}
    </section>
  </main>;
}
