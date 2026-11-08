const id = 'a'.repeat(32);
const finding = { fixed_execution: 'completed', fixed_finding: 'unknown', fixed_rule_ids: [], ai_original_execution: 'completed', ai_original_citations: [], evidence_gaps: [] };
const names = ['configuration','pricing','fulfillment','credit','policy','approval_routing'];
const original = { subject_kind: 'original', subject_id: 'M18-D-B01', business_status: 'needs_revision', specialists: Object.fromEntries(names.map(n => [n,finding])), requested_delivery_date: '2026-09-04', lines: [{line_id:'L1',quantity:10}], availability:[], blockers:[], revision_reasons:[], evidence_gaps:[], uncommitted_paths:[], approval_requirements:[], routing_roles_status:'unavailable_while_route_withheld', required_roles:null };
export const sample = { version: 'source-grounded-review-v1', assessment_id:id, phase1c_pin:'90c0bc8e', phase1c_run_id:id, bundle_sha256:'b'.repeat(64), source_input_digest:'c'.repeat(64), original, candidate:null, candidate_comparison:null, recommendations:[], reviewer_action:'review', permitted_next_actions:[], authorization:'human_only_not_granted' };
export { id, finding, names, original };
