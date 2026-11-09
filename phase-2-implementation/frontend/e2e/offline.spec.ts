import { test, expect } from '@playwright/test';
const base = process.env.DEALDESK_E2E_BASE_URL || 'http://127.0.0.1:3000';
async function enterDemo(page: import('@playwright/test').Page) {
  await page.goto('/');
  if (await page.getByLabel('Operator password').count()) {
    await page.getByLabel('Operator password').fill(process.env.DEALDESK_UI_PASSWORD!);
    await page.getByRole('button',{name:/Enter workspace/}).click();
  }
  await expect(page.getByRole('button',{name:'Run B01/RC01 offline assessment'})).toBeEnabled();
}

test('operator session, CSRF, fresh RC01 and UC02, persisted recovery and no secrets', async ({page,request}) => {
  const unauth = await request.get(`${base}/api/assessments/${'a'.repeat(32)}/status`); expect(unauth.status()).toBe(401);
  const noCsrfLogin = await request.post(`${base}/api/auth/login`, { data:{ password:'not-a-valid-password' }, headers:{Origin:base} }); expect([403,404]).toContain(noCsrfLogin.status());
  await enterDemo(page);
  const loginCookie = (await page.context().cookies()).find(c => c.name === 'dd_operator'); expect(loginCookie?.httpOnly).toBe(true); expect(loginCookie?.sameSite).toBe('Strict');
  const bad = await page.evaluate(async () => (await fetch('/api/assessments',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':'csrfattack123'},body:JSON.stringify({scenario:'B01/RC01'})})).status); expect(bad).toBe(403);
  const csrfValue = await page.evaluate(async () => (await (await fetch('/api/auth/csrf')).json()).csrf);
  const wrongOrigin = await page.request.post(`${base}/api/assessments`,{data:{scenario:'B01/RC01'},headers:{'X-CSRF-Token':csrfValue,'Idempotency-Key':'originattack123','Origin':'http://evil.invalid'}}); expect(wrongOrigin.status()).toBe(403);
  for(const [index, count] of [[0,21],[1,20]] as const) {
    await page.getByRole('button',{name:`Run ${index===0?'B01/RC01':'N01/UC02'} offline assessment`}).click();
    await expect(page).toHaveURL(/\/assessments\/[0-9a-f]{32}/);
    const id = page.url().split('/').at(-1)!;
    console.log(index===0 ? 'RC01 assessment:' : 'UC02 assessment:',id);
    await expect(page.getByText('EVENTS RECORDED').locator('..').locator('strong')).toHaveText(String(count),{timeout:120000});
    await expect(page.getByRole('heading',{name:'Six specialist responsibilities'})).toBeVisible();
    await expect(page.getByRole('heading',{name: index === 0 ? 'A supported schedule is not an accepted deal.' : 'No verified candidate'})).toBeVisible();
    if(index===0) { await expect(page.getByText('supply supported unreserved',{exact:true})).toBeVisible(); await expect(page.getByText('Customer acceptance: pending',{exact:true})).toBeVisible(); await expect(page.getByText('Candidate deterministic checks · V1 only')).toBeVisible(); }
    else await expect(page.getByText(/completed offline-scripted observation is not clearance/)).toBeVisible();
    await page.reload(); await expect(page.getByText('EVENTS RECORDED').locator('..').locator('strong')).toHaveText(String(count),{timeout:120000});
    const [st,ev,rv]=await Promise.all([page.request.get(`${base}/api/assessments/${id}/status`),page.request.get(`${base}/api/assessments/${id}/events?after=0`),page.request.get(`${base}/api/assessments/${id}/review`)]);
    expect(st.status()).toBe(200); expect(ev.status()).toBe(200); expect(rv.status()).toBe(200);
    const events = (await ev.json()).events; expect(events).toHaveLength(count); expect(events.map((e:{sequence:number})=>e.sequence)).toEqual(Array.from({length:count},(_,i)=>i+1));
    expect(events.filter((e:{kind:string})=>e.kind==='fixed_completed')).toHaveLength(6); expect(events.filter((e:{kind:string})=>e.kind==='ai_completed')).toHaveLength(6);
    const r=await rv.json(); expect(r.authorization).toBe('human_only_not_granted'); expect(r.candidate === null).toBe(index===1);
    if(index===0) {
      expect(r.original.lines[0].quantity).toBe(10); expect(r.original.requested_delivery_date).toBe('2026-09-04');
      expect(Number(r.original.availability[0].quantity_by_requested_date)).toBe(8);
      expect(r.candidate_comparison.proposed_slices.map((s:{quantity:number,delivery_date:string})=>[s.quantity,s.delivery_date])).toEqual([[8,'2026-09-03'],[2,'2026-09-08']]);
      expect(r.candidate_comparison.fixed_supply_status).toBe('supply_supported_unreserved');
      expect(r.candidate_comparison.reservation_status).toBe('not_reserved');
      expect(r.candidate_comparison.customer_acceptance).toBe('pending');
      expect(r.candidate_comparison.unmet_customer_constraints).toContain('original_requested_delivery_date');
      expect(r.candidate.business_status).toBe('needs_revision'); expect(r.candidate.required_roles).toBeNull();
      for(const specialist of Object.values(r.candidate.specialists) as {ai_original_execution:string|null}[]) expect(specialist.ai_original_execution).toBeNull();
    } else {
      expect(r.original.specialists.credit.fixed_finding).toBe('unknown');
      expect(r.original.specialists.credit.ai_original_execution).toBe('completed');
      expect(r.original.specialists.credit.evidence_gaps.map((g:{reason_code:string})=>g.reason_code)).toEqual(expect.arrayContaining(['stale','unavailable']));
    }
    const html=await page.content(); expect(html).not.toContain(process.env.DEALDESK_DEMO_TOKEN!); expect(JSON.stringify(r)).not.toContain(process.env.DEALDESK_DEMO_TOKEN!);
    await page.screenshot({path:`/tmp/opencode/d5-${index===0?'rc01':'uc02'}.png`,fullPage:true});
    await page.goto('/'); await page.goBack();
    await expect(page.getByText('EVENTS RECORDED').locator('..').locator('strong')).toHaveText(String(count));
    await page.goForward();
    await page.goto('/');
  }
  for(const width of [390,768,1440]) {
    await page.setViewportSize({width,height:844});
    await expect(page.getByRole('heading',{name:'Explore two synthetic scenarios'})).toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  }
  await page.keyboard.press('Tab'); expect(await page.evaluate(()=>document.activeElement?.tagName)).not.toBe('BODY');
  const token = await page.evaluate(async()=> (await (await fetch('/api/auth/csrf')).json()).csrf);
  const logout = await page.evaluate(async csrf => (await fetch('/api/auth/logout',{method:'POST',headers:{'X-CSRF-Token':csrf}})).status,token); expect(logout).toBe(200);
  await expect.poll(async()=> (await page.request.get(`${base}/api/assessments/${'a'.repeat(32)}/status`)).status()).toBe(401);
});

test('browser hides stale decisions on interruption, invalid response and expired session', async ({page}) => {
  await enterDemo(page);
  await page.getByRole('button',{name:'Run N01/UC02 offline assessment'}).click();
  await expect(page).toHaveURL(/\/assessments\/[0-9a-f]{32}/);
  const id=page.url().split('/').at(-1)!;
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toBeVisible({timeout:120000});
  const path=`**/api/assessments/${id}/status`;
  await page.route(path,route=>route.fulfill({status:503,contentType:'application/json',body:'{"detail":"Offline API unavailable"}'}));
  await expect(page.getByRole('alert').filter({hasText:'Retrying; review withheld'})).toBeVisible({timeout:10000});
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toHaveCount(0);
  await page.unroute(path);
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toBeVisible({timeout:10000});
  await page.route(path,route=>route.fulfill({status:200,contentType:'application/json',body:'{"raw_checkpoint":"PRIVATE-TRACE"}'}));
  await expect(page.getByRole('alert').filter({hasText:'response inconsistent'})).toBeVisible({timeout:10000});
  await expect(page.locator('body')).not.toContainText('PRIVATE-TRACE');
  await page.unroute(path);
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toBeVisible({timeout:10000});
  await page.context().clearCookies();
  await page.reload();
  await expect(page.getByRole('alert').filter({hasText:'Operator session expired'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toHaveCount(0);
  await expect(page.getByRole('link',{name:'Return to homepage'})).toBeVisible();
});
