import { describe, expect, it } from 'vitest';
import { Created, Events, Review, Status } from '../lib/contracts';
import { id, finding, names, original, sample } from './fixture';
const base = { version: 'demo-api-v1', assessment_id: id, scenario: 'B01/RC01', mode: 'offline_scripted', status: 'completed', last_sequence: 1, phase1c_pin: '90c0bc8e' };
describe('strict D3 / D2 contracts', () => {
  it('accepts status and keeps null candidate and roles', () => { expect(Status.parse(base)).toEqual(base); expect(Review.parse(sample).original.required_roles).toBeNull(); });
  it('rejects version drift, added fields, mode changes and invalid timestamps', () => {
    expect(Status.safeParse({...base, version:'demo-api-v2'}).success).toBe(false);
    expect(Created.safeParse({...base, created:true, token:'secret'}).success).toBe(false);
    expect(Status.safeParse({...base,mode:'hosted'}).success).toBe(false);
    expect(Events.safeParse({version:'demo-api-v1',assessment_id:id,events:[{assessment_id:id,sequence:1,kind:'checkpoint',stage:'candidate',occurred_at:'yesterday'}]}).success).toBe(false);
  });
  it('rejects review drift, candidate mismatch and invented AI on candidate', () => {
    expect(Review.safeParse({...sample, raw_checkpoint:{}}).success).toBe(false);
    expect(Review.safeParse({...sample, candidate_comparison:{}}).success).toBe(false);
    const candidate = {...original,subject_kind:'candidate',subject_id:'C1',specialists:Object.fromEntries(names.map(n => [n,{...finding,ai_original_execution:'completed'}]))};
    expect(Review.safeParse({...sample,candidate}).success).toBe(false);
    expect(Review.safeParse({...sample,original:{...original,required_roles:[]}}).success).toBe(false);
  });
});
