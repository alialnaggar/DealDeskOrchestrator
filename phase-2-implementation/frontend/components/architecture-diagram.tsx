const responsibilities = [
  'Configuration Validator',
  'Pricing & Discounting',
  'Availability, Production & Fulfillment',
  'Credit & Risk',
  'Policy & Compliance',
  'Approval Routing & Escalation'
] as const;

function Arrow() { return <span className="flow-arrow" aria-hidden="true" />; }

export function ArchitectureDiagram() {
  return <section className="architecture panel" aria-labelledby="architecture-title" aria-describedby="architecture-note">
    <div className="architecture-heading"><div><span className="eyebrow">INTENDED SYSTEM ARCHITECTURE</span><h2 id="architecture-title">From request to human decision</h2></div><span className="architecture-label">Decision support · not approval</span></div>
    <ol className="flow" aria-label="Deal assessment architecture">
      <li className="flow-stage request-stage"><span className="stage-symbol" aria-hidden="true">↗</span><strong>Deal Request</strong></li>
      <li aria-hidden="true"><Arrow /></li>
      <li className="flow-stage orchestrator-stage"><span className="stage-symbol" aria-hidden="true">◇</span><strong>Multi-Agent Orchestrator</strong></li>
      <li aria-hidden="true"><Arrow /></li>
      <li className="specialist-group"><div className="specialist-group-title">Six specialist responsibilities</div><ol className="specialist-grid">{responsibilities.map((name, i) => <li className="specialist-node" key={name}><span className="specialist-number" aria-hidden="true">{String(i + 1).padStart(2,'0')}</span><strong>{name}</strong></li>)}</ol></li>
      <li aria-hidden="true"><Arrow /></li>
      <li className="flow-stage assessment-stage"><span className="stage-symbol" aria-hidden="true">≡</span><strong>Consolidated Assessment</strong></li>
      <li aria-hidden="true"><Arrow /></li>
      <li className="flow-stage human-stage"><span className="stage-symbol" aria-hidden="true">H</span><strong>Human Decision</strong></li>
    </ol>
    <p id="architecture-note" className="architecture-note">Architecture shown above. This demo runs two offline-scripted synthetic scenarios—not six independent live AI calls. Only people can approve a deal.</p>
  </section>;
}
