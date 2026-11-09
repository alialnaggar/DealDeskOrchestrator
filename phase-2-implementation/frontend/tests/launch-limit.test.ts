import { describe, expect, it } from 'vitest';
import { createLaunchLimiter } from '../lib/launch-limit';

describe('public synthetic launch cap', () => {
  it('preserves idempotent retries but caps new assessments per session', () => {
    const allow=createLaunchLimiter();
    for(let i=0;i<4;i++) expect(allow('one',`key${i}`,100_000)).toBe(true);
    expect(allow('one','key0',100_001)).toBe(true);
    expect(allow('one','key4',100_002)).toBe(false);
    expect(allow('one','key4',160_003)).toBe(true);
  });
  it('shares the global creation cap across anonymous sessions', () => {
    const allow=createLaunchLimiter();
    for(let i=0;i<8;i++) expect(allow(`session${i}`,'key',100_000)).toBe(true);
    expect(allow('session8','key',100_001)).toBe(false);
    expect(allow('session8','key',160_002)).toBe(true);
  });
});
