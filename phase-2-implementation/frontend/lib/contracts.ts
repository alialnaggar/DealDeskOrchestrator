import { z } from 'zod';

const id = z.string().regex(/^[0-9a-f]{32}$/);
const code = z.string().min(1).max(200);
const date = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const specialists = ['configuration', 'pricing', 'fulfillment', 'credit', 'policy', 'approval_routing'] as const;
export { specialists };
const specialist = z.enum(specialists);
const status = z.object({ version: z.literal('demo-api-v1'), assessment_id: id, scenario: z.enum(['B01/RC01','N01/UC02']), mode: z.literal('offline_scripted'), status: z.enum(['accepted','running','completed','stopped','uncertain']), last_sequence: z.number().int().nonnegative(), phase1c_pin: code }).strict();
export const Status = status;
export const Created = status.extend({ created: z.boolean() }).strict();
export const Event = z.object({ assessment_id: id, sequence: z.number().int().positive(), occurred_at: z.string().datetime({ offset: true }), kind: z.enum(['accepted','running','preflight_ok','checkpoint','fixed_completed','ai_completed','review_ready','stopped','uncertain']), stage: z.enum([...specialists,'original','candidate','review']).nullable() }).strict();
export const Events = z.object({ version: z.literal('demo-api-v1'), assessment_id: id, events: z.array(Event).max(100) }).strict();
const gap = z.object({ requirement_id: code, reason_code: code, verification: code, impact_code: code, next_action_code: code }).strict();
const finding = z.object({ fixed_execution: code, fixed_finding: code, fixed_rule_ids: z.array(code), ai_original_execution: code.nullable(), ai_original_citations: z.array(z.object({ ref: code, field: code }).strict()), evidence_gaps: z.array(gap) }).strict();
const subject = z.object({ subject_kind: z.enum(['original','candidate']), subject_id: code, business_status: code, specialists: z.object(Object.fromEntries(specialists.map(s => [s, finding])) as Record<typeof specialists[number], typeof finding>).strict(), requested_delivery_date: date, lines: z.array(z.object({ line_id: code, quantity: z.number().int().positive() }).strict()), availability: z.array(z.object({ line_id: code, status: code, requested_quantity: z.number().int(), quantity_by_requested_date: z.string(), earliest_full_date: date.nullable() }).strict()), blockers: z.array(z.union([z.object({ code: code, line_id: code.nullable() }).strict(), z.object({ code: code, rule_id: code, specialist }).strict()])), revision_reasons: z.array(z.object({ code, line_id: code.nullable() }).strict()), evidence_gaps: z.array(code), uncommitted_paths: z.array(code), approval_requirements: z.array(z.object({ rule_id: code, severity: code }).strict()), routing_roles_status: code, required_roles: z.array(z.object({ rule_id: code, role: code, sequence: z.number().int() }).strict()).nullable() }).strict();
const comparison = z.object({ parent_subject_id: code, candidate_id: code, candidate_input_digest: code, changed_field: z.literal('proposed_delivery_slices'), original_line_id: code, original_quantity: z.number().int().positive(), original_requested_date: date, proposed_slices: z.array(z.object({ quantity: z.number().int().positive(), delivery_date: date, source_refs: z.array(code) }).strict()), fixed_supply_status: code, reservation_status: z.literal('not_reserved'), customer_acceptance: z.literal('pending'), unmet_customer_constraints: z.array(code), addressed_original_reasons: z.array(code), remaining_revision_reasons: z.array(code) }).strict();
export const Review = z.object({ version: z.literal('source-grounded-review-v1'), assessment_id: id, phase1c_pin: code, phase1c_run_id: code, bundle_sha256: code, source_input_digest: code, original: subject, candidate: subject.nullable(), candidate_comparison: comparison.nullable(), recommendations: z.array(z.object({ specialist, action_code: code, verification: z.enum(['deterministic','suggested_unverified']), subject_id: code, source_refs: z.array(code), rule_ids: z.array(code), remaining_customer_constraints: z.array(code) }).strict()), reviewer_action: code, permitted_next_actions: z.array(code), authorization: z.literal('human_only_not_granted') }).strict().superRefine((r, ctx) => {
  if ((r.candidate === null) !== (r.candidate_comparison === null) || r.original.subject_kind !== 'original' || r.candidate?.subject_kind === 'original' || (r.candidate && (r.candidate_comparison?.candidate_id !== r.candidate.subject_id || r.candidate_comparison.parent_subject_id !== r.original.subject_id))) ctx.addIssue({ code: 'custom', message: 'Subject lineage mismatch' });
  if (r.candidate && specialists.some(s => r.candidate!.specialists[s].ai_original_execution !== null)) ctx.addIssue({ code: 'custom', message: 'Candidate AI is not part of this contract' });
  for (const subject of [r.original, r.candidate].filter((s): s is NonNullable<typeof s> => s !== null)) {
    if ((subject.required_roles === null) !== (subject.routing_roles_status === 'unavailable_while_route_withheld')) ctx.addIssue({code:'custom',message:'Withheld routing role status mismatch'});
  }
  if (r.candidate && r.candidate_comparison) {
    const c = r.candidate_comparison;
    const line = r.original.lines.find(l => l.line_id === c.original_line_id);
    if (!line || line.quantity !== c.original_quantity || c.original_requested_date !== r.original.requested_delivery_date || r.candidate.requested_delivery_date !== r.original.requested_delivery_date || c.proposed_slices.reduce((sum, slice) => sum + slice.quantity, 0) !== c.original_quantity || JSON.stringify(r.candidate.lines) !== JSON.stringify(r.original.lines)) ctx.addIssue({code:'custom',message:'Original and candidate quantity/date mismatch'});
  }
});
export type StatusDTO = z.infer<typeof Status>;
export type EventDTO = z.infer<typeof Event>;
export type ReviewDTO = z.infer<typeof Review>;
