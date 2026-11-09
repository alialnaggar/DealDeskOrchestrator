import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Review, type EventDTO } from '../lib/contracts';
import { Comparison, DecisionBrief, EvidenceReview, HumanReview, SpecialistMatrix, Timeline } from '../components/workspace';
import { assessmentLabel, assessmentTone } from '../lib/presentation';
import { finding, names, original, sample } from './fixture';
const parsed = Review.parse(sample);
describe('business presentation', () => {
  it('distinguishes no candidate from unknown fixed Credit and completed AI', () => {
    render(<Comparison data={parsed}/>);
    expect(screen.getByText('No verified candidate')).toBeTruthy();
    expect(screen.getByText(/completed offline-scripted observation is not clearance/)).toBeTruthy();
  });
  it('does not invent a completed Credit observation when it abstained or is null', () => {
    for(const execution of ['abstained', null]) {
      const data = Review.parse({...sample,original:{...original,specialists:{...original.specialists,credit:{...finding,ai_original_execution:execution}}}});
      const {container,unmount} = render(<Comparison data={data}/>);
      expect(container.textContent).not.toContain('a completed offline-scripted observation');
      expect(container.textContent).toContain(execution === 'abstained' ? 'observation abstained' : 'no offline-scripted Credit outcome is available');
      unmount();
    }
  });
  it('does not turn checkpointed AI into a positive finding', () => {
    const event: EventDTO = { assessment_id:sample.assessment_id,sequence:1,kind:'ai_completed',stage:'credit',occurred_at:'2026-11-08T12:00:00Z' };
    const { container } = render(<SpecialistMatrix data={null} rows={[event]}/>);
    expect(container.textContent).toContain('Checkpointed · outcome pending review');
    expect(container.textContent).toContain('Pending');
  });
  it('shows six deterministic candidate checks, unreserved supply and pending acceptance', () => {
    const candidate = {...original,subject_kind:'candidate',subject_id:'C1',specialists:Object.fromEntries(names.map(n => [n,{...finding,ai_original_execution:null}]))};
    const comparison = { parent_subject_id:original.subject_id,candidate_id:'C1',candidate_input_digest:'digest',changed_field:'proposed_delivery_slices',original_line_id:'L1',original_quantity:10,original_requested_date:'2026-09-04',proposed_slices:[{quantity:8,delivery_date:'2026-09-03',source_refs:['inventory:I1']},{quantity:2,delivery_date:'2026-09-08',source_refs:['inbound_supply:S1']}],fixed_supply_status:'supply_supported_unreserved',reservation_status:'not_reserved',customer_acceptance:'pending',unmet_customer_constraints:['original_requested_delivery_date'],addressed_original_reasons:[],remaining_revision_reasons:['partial_delivery_requires_customer_acceptance'] };
    const data = Review.parse({...sample,candidate,candidate_comparison:comparison});
    const {container} = render(<><DecisionBrief data={data}/><Comparison data={data}/></>);
    expect(container.textContent).toContain('supply supported unreserved'); expect(container.textContent).toContain('Customer acceptance: pending');
    expect(container.querySelectorAll('.checks-grid > div')).toHaveLength(6);
    expect(screen.getByRole('heading',{name:'A later delivery needs the customer’s decision'})).toBeTruthy();
    expect(container.textContent).toContain('10 units'); expect(container.textContent).toContain('4 Sept 2026');
    expect(container.textContent).toContain('8 on 3 Sept 2026 + 2 on 8 Sept 2026');
    expect(container.textContent).toContain('No stock is reserved');
  });
  it('summarizes unknown Credit without presenting scripted completion as clearance', () => {
    const data = Review.parse({...sample,original:{...original,specialists:{...original.specialists,credit:{...finding,fixed_finding:'unknown'}}}});
    const {container} = render(<DecisionBrief data={data}/>);
    expect(container.textContent).toContain('Fixed Credit is unknown');
    expect(container.textContent).toContain('None verified');
    expect(container.textContent).toContain('No approval is granted here');
  });
  it('shows validated abstention and evidence gap, withholds routing and leaves actions human-only', () => {
    const review = Review.parse({...sample, original:{...sample.original,specialists:{...sample.original.specialists,credit:{...sample.original.specialists.credit,ai_original_execution:'abstained',evidence_gaps:[{requirement_id:'credit_source',reason_code:'stale',verification:'deterministic',impact_code:'unknown',next_action_code:'review'}]}}}});
    const { container } = render(<><SpecialistMatrix data={review} rows={[{assessment_id:review.assessment_id,sequence:1,occurred_at:'2026-11-09T00:00:00Z',kind:'fixed_completed',stage:'credit'},{assessment_id:review.assessment_id,sequence:2,occurred_at:'2026-11-09T00:00:01Z',kind:'ai_completed',stage:'credit'}]}/><HumanReview data={review}/></>);
    expect(container.textContent).toContain('abstained'); expect(container.textContent).toContain('stale'); expect(container.textContent).toContain('route withheld'); expect(container.textContent).toContain('human only not granted');
    expect(screen.queryByRole('button', {name:/approve|reserve|accept/i})).toBeNull();
  });
  it('distinguishes withheld null roles from an empty eligible role list', () => {
    const unavailable = render(<HumanReview data={parsed}/>);
    expect(unavailable.container.textContent).toContain('Required roles: unavailable while routing is withheld');
    unavailable.unmount();
    const eligible = Review.parse({...sample,original:{...sample.original,routing_roles_status:'available_from_fixed_interface',required_roles:[]}});
    const available = render(<HumanReview data={eligible}/>);
    expect(available.container.textContent).toContain('Required roles: none returned by the fixed interface');
    expect(available.container.textContent).not.toContain('Required roles: unavailable');
  });
  it('preserves long cited refs and does not invent an empty source', () => {
    const ref='inventory:'+ 'x'.repeat(185);
    const entry={specialist:'fulfillment',action_code:'human_review',verification:'deterministic',subject_id:original.subject_id,source_refs:[ref],rule_ids:[],remaining_customer_constraints:[]};
    const data=Review.parse({...sample,recommendations:[entry,{...entry,source_refs:[]}]});
    const {container}=render(<HumanReview data={data}/>);
    expect(container.textContent).toContain(ref);
    expect(container.querySelectorAll('.recommendations small')[1].textContent).not.toContain('sources');
  });
  it('renders real checkpoint and timestamp only from events', () => {
    render(<Timeline rows={[{ assessment_id:sample.assessment_id,sequence:1,kind:'checkpoint',stage:'original',occurred_at:'2026-11-08T12:00:00Z' }]} data={null} state={null}/>);
    expect(screen.getByText('Checkpoint stored')).toBeTruthy(); expect(screen.getByText(/8 Nov 2026/)).toBeTruthy();
  });
  it('never labels completed execution as clearance', () => {
    expect(assessmentLabel.completed).toContain('review required');
    expect(assessmentTone.completed).toBe('neutral');
    expect(assessmentLabel.uncertain).toContain('uncertain');
  });
  it('shows only validated original evidence and explicit missing information', () => {
    const gap = {requirement_id:'current_credit',reason_code:'stale',verification:'unknown',impact_code:'blocked',next_action_code:'request_current_evidence'};
    const data = Review.parse({...sample,original:{...original,specialists:{...original.specialists,credit:{...finding,fixed_rule_ids:['CR-1'],evidence_gaps:[gap]}}}});
    const {container} = render(<EvidenceReview data={data}/>);
    expect(container.textContent).toContain('Credit & risk · stale');
    expect(container.textContent).toContain('request current evidence');
    expect(container.textContent).toContain('CR-1');
  });
});
