// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
vi.mock('server-only',()=>({}));
import { DealInput, supportedInputs, supportedMatch } from '../lib/intake-contract';
import { matchAuthoritativeFixture } from '../lib/intake-server';
import { GET as sessionToken } from '../app/api/auth/csrf/route';
import { POST as match } from '../app/api/intake/match/route';
import { sessionFromCookie, verifyIntakeReceipt } from '../lib/security';
import { createIntakeLimiter } from '../lib/intake-limit';

const origin='https://dealdeskdemo.duckdns.org';
beforeEach(()=>{process.env.DEALDESK_UI_ORIGIN=origin;process.env.DEALDESK_PUBLIC_SYNTHETIC_DEMO='1';process.env.DEALDESK_UI_SESSION_SECRET='private-test-secret-at-least-thirty-two-characters';});
afterEach(()=>{for(const name of ['DEALDESK_UI_ORIGIN','DEALDESK_PUBLIC_SYNTHETIC_DEMO','DEALDESK_UI_SESSION_SECRET']) delete process.env[name];});
describe('authoritative synthetic intake',()=>{
  it('checks both fixture hashes and every commercial input, not just IDs',()=>{
    for(const key of ['rc01','uc02'] as const) {
      const input=supportedInputs[key];expect(matchAuthoritativeFixture(input)).toBe(key);
      for(const field of Object.keys(input) as (keyof typeof input)[]) {
        const change={...input,[field]:field==='configuration'?{size:'modified'}:field==='contractClauseCodes'?['other']:field==='allowPartialDelivery'?!input.allowPartialDelivery:field==='discountPercent'?0:field==='additionalRequirements'?'Needs extra commitment':field==='requestedDeliveryDate'?'2026-09-05':field==='destinationCountryCode'?'FR':field==='currencyCode'?'USD':typeof input[field]==='number'?Number(input[field])+1:`${input[field]}-changed`};
        expect(supportedMatch(DealInput.parse(change))).toBeNull();
      }
    }
  });
  it('rejects malformed dates, negative prices and unexpected properties',()=>{
    expect(DealInput.safeParse({...supportedInputs.rc01,requestedDeliveryDate:'2026-02-31'}).success).toBe(false);
    expect(DealInput.safeParse({...supportedInputs.rc01,quotedUnitPrice:-1}).success).toBe(false);
    expect(DealInput.safeParse({...supportedInputs.rc01,scenario:'B01/RC01'}).success).toBe(false);
  });
  it('bounds public matching separately from assessment creation',()=>{
    const allow=createIntakeLimiter();for(let i=0;i<20;i++) expect(allow('one',100_000)).toBe(true);
    expect(allow('one',100_000)).toBe(false);expect(allow('two',100_000)).toBe(true);
    expect(allow('one',160_001)).toBe(true);
  });
  it('requires a signed session/CSRF; unmatched deals are not recorded or launched',async()=>{
    const login=await sessionToken(new NextRequest(origin+'/api/auth/csrf'));
    const {csrf}=await login.json();const cookie=login.cookies.get('dd_operator')!.value;
    const send=(data:unknown,headers:Record<string,string>={})=>match(new NextRequest(origin+'/api/intake/match',{method:'POST',headers:{Host:'dealdeskdemo.duckdns.org',Origin:origin,Cookie:`dd_operator=${cookie}`,'X-CSRF-Token':csrf,'Content-Type':'application/json',...headers},body:JSON.stringify(data)}));
    expect((await match(new NextRequest(origin+'/api/intake/match',{method:'POST',body:JSON.stringify(supportedInputs.rc01)}))).status).toBe(401);
    expect((await send(supportedInputs.rc01,{'Origin':'https://evil.invalid'})).status).toBe(403);
    const unsupported=await send({...supportedInputs.rc01,quotedUnitPrice:901});expect(await unsupported.json()).toEqual({matched:false});
    const ok=await send(supportedInputs.uc02);const result=await ok.json();expect(result.matched).toBe(true);expect(result.scenario).toBe('uc02');
    const nonce=sessionFromCookie(cookie);expect(verifyIntakeReceipt(result.receipt,nonce)?.scenario).toBe('uc02');
    expect(verifyIntakeReceipt(result.receipt, 'a'.repeat(64))).toBeNull();
    expect(verifyIntakeReceipt(result.receipt.replace('uc02','rc01'),nonce)).toBeNull();
  });
});
