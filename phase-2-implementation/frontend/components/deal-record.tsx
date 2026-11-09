import { guides, responsibilities, type GuideKey } from '@/lib/scenario-guide';
import type { ReviewDTO } from '@/lib/contracts';

const recordFields = (key: GuideKey) => {
  const g = guides[key];
  return [
    { heading: 'Parties & identification', fields: [['Customer ID', g.customer], ['Deal ID', g.deal], ['Fixture customer label', key === 'rc01' ? 'Disposable B01' : 'Disposable N01'], ['Record', 'M1.8 provisional case · generated_test · Submitted'], ['Executed legal contract', 'Not present in fixture']] },
    { heading: 'Commercial request', fields: [['Product ID', g.product], ['Line ID', g.line], ['Configuration', 'Empty configuration object in fixture'], ['Quantity', `${g.quantity} units`], ['Requested delivery', '04 Sep 2026'], ['Quoted unit price', '€900'], ['Currency', 'EUR'], ['Discount', 'Not specified in fixture'], ['Payment terms', '30 days']] },
    { heading: 'Supply & policy', fields: [['Inventory evidence', g.stock], ['Inbound evidence', g.inbound], ['Shipping', 'Standard · destination Berlin, DE · 2 transit workdays'], ['Partial delivery', g.partial], ['Policy set', 'BASELINE_2026'], ['Catalog', 'CATALOGUE_2026_V1'], ['Contract clause', 'standard'], ['Approval outcome', 'Not available before assessment']] },
    { heading: 'Credit & source references', fields: [['Credit fixture', g.credit], ['Evidence record IDs', g.refs.join(' · ')], ['Signed agreement or customer acceptance', 'Not present in fixture']] }
  ];
};

export function DealRecord({ scenario, candidate }: { scenario: GuideKey; candidate?: ReviewDTO }) {
  const c = candidate?.candidate_comparison;
  return <section id="deal-record" className="panel deal-document" aria-labelledby={c ? 'candidate-record-title' : 'deal-record-title'}>
    <div className="document-header"><div><span className="eyebrow">SYNTHETIC FIXTURE · {c ? 'CHECKED CANDIDATE V1' : 'ORIGINAL REQUEST V0'}</span><h2 id={c ? 'candidate-record-title' : 'deal-record-title'}>{c ? 'Revised deal record' : 'Structured deal record'}</h2></div><span className="scenario-code">{guides[scenario].deal}</span></div>
    <p className="section-guide">{c ? 'The original fields below remain unchanged; only the proposed delivery slices differ. This is not an accepted order.' : 'Source: disposable M1.8 fixture and M2.1 credit overlay; this is not an executed legal contract or a live database read.'}</p>
    {c && <div className="document-change"><strong>Changed · proposed delivery slices</strong><p>{c.proposed_slices.map(s => `${s.quantity} units on ${s.delivery_date} (${s.source_refs.join(', ')})`).join(' + ')}</p><small>Original requested date remains {c.original_requested_date}; customer acceptance {c.customer_acceptance}; {c.reservation_status.replaceAll('_',' ')}.</small></div>}
    <div className="document-grid">{recordFields(scenario).map(section => <section key={section.heading}><h3>{section.heading}</h3><dl>{section.fields.map(([name,value]) => <div key={name}><dt>{name}</dt><dd>{value}</dd></div>)}</dl></section>)}</div>
  </section>;
}

export function ResponsibilityFlow({ focus }: { focus: string }) {
  return <section className="panel responsibility-flow" aria-labelledby="flow-title"><span className="eyebrow">RESPONSIBILITY MAP · V0</span><h2 id="flow-title">Six specialists, one governed assessment</h2><p className="section-guide">The fixed original checks are recorded first. Scripted original-subject inspections follow recorded checkpoints; this visual map is not a promise of six live or strictly sequential AI calls.</p><ol>{responsibilities.map((r,i) => <li key={r.key} className={r.name === focus ? 'focus-specialist' : ''}><div><span className="index">{String(i+1).padStart(2,'0')}</span><h3>{r.name}</h3>{r.name === focus && <span className="status warning">Scenario focus</span>}</div><p><strong>Inputs:</strong> {r.inputs}</p><p><strong>Checks:</strong> {r.check}</p><p><strong>Output:</strong> {r.output}</p><small>Escalate when: {r.escalation}</small></li>)}</ol></section>;
}
