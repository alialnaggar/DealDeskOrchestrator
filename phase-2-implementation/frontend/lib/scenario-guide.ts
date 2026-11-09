// Public, synthetic fixture preview. Values below are transcribed from
// backend/tests/m18_case_setup.py and m21_integrated_credit_setup.py; no
// pre-run source-record API exists. Never treat this as a live database read.
export const guides = {
  rc01: {
    code: 'B01/RC01', title: 'Delivery Constraint & Revised Proposal', focus: 'Availability, Production & Fulfillment',
    description: 'A customer deal encounters a delivery constraint. A revised delivery proposal is evaluated against available evidence and business rules, while customer acceptance and human authority remain unresolved.',
    traits: ['Original request versus possible revision', 'Delivery feasibility & validation', 'Evidence-backed checks', 'Customer acceptance & human review'],
    objective: 'Test whether an inspected delivery alternative can be checked against the pinned source and fixed rules without treating a proposal as an accepted order.',
    risk: 'Requested delivery timing; partial delivery needs customer acceptance. No reservation or approval is implied.',
    customer: 'M18-C-B01', deal: 'M18-D-B01', product: 'M18-P-B01', line: 'M18-L-B01', quantity: 10,
    stock: '20 on hand; 12 allocated (snapshot 01 Sep 2026, 10:00 UTC)', inbound: '5 inbound; 2 allocated, confirmed for 03 Sep 2026',
    credit: 'RC01 fixture: €10,000 limit; €100 committed; current commitments, Active status. Receivable €60 outstanding; payment €40 recorded.',
    partial: 'Permitted in source terms', refs: ['M18-INV-B01', 'M18-IN-B01', 'M18-BIND-B01', 'M21IC-AR-RC01', 'M21IC-PAY-RC01']
  },
  uc02: {
    code: 'N01/UC02', title: 'Credit Evidence Gap & Unresolved Deal', focus: 'Credit & Risk',
    description: 'A deal is assessed with insufficient credit evidence. The system must identify missing information, avoid unsupported clearance and communicate the required next action without inventing an acceptable alternative.',
    traits: ['Missing credit evidence', 'Evidence sufficiency & risk checks', 'No verified revised candidate', 'Uncertainty & required follow-up'],
    objective: 'Test evidence-sufficiency handling: a scripted observation must not substitute for a supported fixed credit finding or authorize a revision.',
    risk: 'Credit commitments are stale and receivable/payment rows are unavailable; source terms prohibit partial delivery.',
    customer: 'M18-C-N01', deal: 'M18-D-N01', product: 'M18-P-N01', line: 'M18-L-N01', quantity: 10,
    stock: '20 on hand; 12 allocated (snapshot 01 Sep 2026, 10:00 UTC)', inbound: '5 inbound; 2 allocated, confirmed for 03 Sep 2026',
    credit: 'UC02 fixture: €5,000 limit; €300 committed (as of 01 Aug 2026); High risk, Review status. Receivable and payment rows unavailable.',
    partial: 'Not permitted in source terms', refs: ['M18-INV-N01', 'M18-IN-N01', 'M18-BIND-N01']
  }
} as const;
export type GuideKey = keyof typeof guides;
export const guideForCode = (code: string) => code === 'B01/RC01' ? guides.rc01 : code === 'N01/UC02' ? guides.uc02 : null;

export const responsibilities = [
  { key: 'configuration', name: 'Configuration Validator', inputs: 'Product, configuration and catalog', check: 'Sellability and configuration mapping', output: 'Fixed finding and rule references', escalation: 'Invalid or unsupported configuration' },
  { key: 'pricing', name: 'Pricing & Discounting', inputs: 'Quoted unit price, product cost and policy', check: 'Fixed pricing and margin calculations', output: 'Fixed finding and rule references', escalation: 'Rule or margin constraint' },
  { key: 'fulfillment', name: 'Availability, Production & Fulfillment', inputs: 'Line, stock, inbound supply and shipping lane', check: 'Availability, delivery timing and verified proposal where possible', output: 'Fixed supply finding; optional scripted proposal', escalation: 'Delivery constraint or customer acceptance' },
  { key: 'credit', name: 'Credit & Risk', inputs: 'Credit profile, commitments, receivables and payments', check: 'Exposure and evidence freshness', output: 'Fixed finding or unknown with evidence gaps', escalation: 'Stale or missing credit evidence' },
  { key: 'policy', name: 'Policy & Compliance', inputs: 'Policy set and fixed specialist outcomes', check: 'Applicable rule identifiers and unmet constraints', output: 'Fixed policy finding', escalation: 'Unmet policy requirement' },
  { key: 'approval_routing', name: 'Approval Routing & Escalation', inputs: 'Fixed findings and approval policy', check: 'Route and eligible roles when available', output: 'Required roles or withheld route', escalation: 'Unresolved gate; never grants approval' }
] as const;
