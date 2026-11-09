import { expect, test } from '@playwright/test';

test('fresh supervisor walkthrough: source-grounded brief, mobile, recovery and technical trace', async ({ page }) => {
  test.setTimeout(180000);
  const root = process.env.DEALDESK_E2E_BASE_URL || 'http://127.0.0.1:3000';
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'From request to responsible decision.'})).toBeVisible();
  await expect(page.locator('.specialist-node')).toHaveCount(6);
  if (root === 'https://dealdeskdemo.duckdns.org') {
    await expect(page.getByLabel('Operator password')).toHaveCount(0);
    await expect(page.getByRole('button',{name:/sign in|log in|enter workspace/i})).toHaveCount(0);
    expect((await page.request.post(`${root}/api/auth/login`,{data:{password:'public-mode-disabled'}})).status()).toBe(404);
  }
  if (await page.getByLabel('Operator password').count()) {
    await page.getByLabel('Operator password').fill(process.env.DEALDESK_UI_PASSWORD!);
    await page.getByRole('button', { name:/Enter workspace/ }).click();
  }
  await expect(page.getByRole('heading',{name:'Explore Scenarios'})).toBeVisible();
  await expect(page.getByRole('link',{name:'Explore Scenario B01/RC01'})).toBeEnabled();
  await page.screenshot({path:'/tmp/opencode/dealdesk-home-desktop.png',fullPage:true});
  for (const [width, columns, suffix] of [[820,2,'tablet'],[390,1,'mobile']] as const) {
    await page.setViewportSize({width,height:900});
    await expect.poll(() => page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(await page.locator('.specialist-grid').evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length)).toBe(columns);
    await page.screenshot({path:`/tmp/opencode/dealdesk-home-${suffix}.png`,fullPage:true});
  }
  await page.setViewportSize({width:1440,height:900});
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toBeVisible();
  await page.emulateMedia({reducedMotion:'reduce'});
  expect(await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches)).toBe(true);
  for (const [scenario, count] of [['B01/RC01',21],['N01/UC02',20]] as const) {
    await page.getByRole('link',{name:`Explore Scenario ${scenario}`}).click();
    await expect(page.getByRole('heading',{name:'Structured deal record'})).toBeVisible();
    await expect(page.getByRole('heading',{name:'Six specialists, one governed assessment'})).toBeVisible();
    await expect(page.getByRole('heading',{name:'No verified candidate'})).toHaveCount(0);
    await page.getByRole('button',{name:/Run Assessment/}).click();
    await expect(page).toHaveURL(/\/assessments\/[0-9a-f]{32}/);
    const id=page.url().split('/').at(-1)!;
    await expect(page.getByRole('heading',{name:scenario === 'B01/RC01' ? 'A later delivery needs the customer’s decision' : 'Evidence is insufficient for a verified alternative'})).toBeVisible({timeout:120000});
    await expect(page.getByText('EVENTS RECORDED').locator('..').locator('strong')).toHaveText(String(count));
    const brief=page.locator('.decision-brief');
    await expect(brief).toContainText('needs revision');
    await expect(brief).toContainText('No approval is granted here');
    if(scenario === 'B01/RC01') {
      await expect(brief).toContainText('10 units'); await expect(brief).toContainText('4 Sept 2026');
      await expect(brief).toContainText('8 on 3 Sept 2026 + 2 on 8 Sept 2026');
      await expect(brief).toContainText('No stock is reserved'); await expect(brief).toContainText('Customer acceptance: pending');
      await expect(page.getByRole('heading',{name:'Candidate deterministic checks · V1 only'})).toBeVisible();
    } else {
      await expect(brief).toContainText('Fixed Credit is unknown'); await expect(brief).toContainText('None verified');
      await expect(page.getByRole('heading',{name:'No verified candidate'})).toBeVisible();
      await expect(page.getByText('Evidence gaps: stale, unavailable.')).toBeVisible();
    }
    await expect(page.getByRole('heading',{name:'Six specialist responsibilities'})).toBeVisible();
    await expect(page.locator('.business-specialist-card')).toHaveCount(6);
    await expect(page.getByRole('heading',{name:'Available Evidence & Outstanding Information'})).toBeVisible();
    await expect(page.locator('.business-specialist-card').filter({has:page.getByRole('heading',{name:'Credit & Risk'})})).toContainText(scenario === 'B01/RC01' ? 'Verification limited' : 'Insufficient evidence');
    await expect(page.locator('.business-specialist-card').filter({has:page.getByRole('heading',{name:'Approval Routing & Escalation'})})).toContainText('Routing withheld');
    await page.locator('.business-specialist-card').filter({has:page.getByRole('heading',{name:'Credit & Risk'})}).locator('details').first().locator('summary').click();
    await expect(page.locator('.business-specialist-card').filter({has:page.getByRole('heading',{name:'Credit & Risk'})})).toContainText('ledger completeness');
    await expect(page.getByRole('heading',{name:'Review, not authorization'})).toBeVisible();
    const trace=page.locator('details.trace-details');
    await expect(trace).not.toHaveAttribute('open');
    await trace.locator('summary').focus(); await page.keyboard.press('Enter');
    await expect(trace).toHaveAttribute('open','');
    await expect(trace.locator('ol.timeline li')).toHaveCount(count);
    await trace.locator('summary').click();
    await page.screenshot({path:`/tmp/opencode/d6-${scenario === 'B01/RC01' ? 'rc01' : 'uc02'}-desktop.png`,fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await expect.poll(() => page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(brief).toBeVisible();
    await page.screenshot({path:`/tmp/opencode/d6-${scenario === 'B01/RC01' ? 'rc01' : 'uc02'}-mobile.png`,fullPage:true});
    await page.setViewportSize({width:1440,height:900});
    await page.setViewportSize({width:768,height:900});
    await expect.poll(() => page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.setViewportSize({width:1440,height:900});
    await page.reload(); await expect(brief).toBeVisible();
    const [events,review]=await Promise.all([page.request.get(`${root}/api/assessments/${id}/events?after=0`),page.request.get(`${root}/api/assessments/${id}/review`)]);
    expect(events.status()).toBe(200); expect((await events.json()).events.map((e:{sequence:number})=>e.sequence)).toEqual(Array.from({length:count},(_,i)=>i+1));
    expect(review.status()).toBe(200); expect((await review.json()).assessment_id).toBe(id);
    expect(JSON.stringify(await review.json())).not.toContain(process.env.DEALDESK_DEMO_TOKEN!);
    console.log('D6 fresh', scenario,id,count);
    if(scenario === 'B01/RC01') {
      const path=`**/api/assessments/${id}/status`;
      await page.route(path, route=>route.fulfill({status:503,contentType:'application/json',body:'{"detail":"Internal private failure"}'}));
      await expect(page.getByRole('alert').filter({hasText:'review withheld'})).toBeVisible({timeout:10000});
      await expect(brief).toHaveCount(0);
      await expect(page.getByRole('button',{name:'Retry now'})).toBeVisible();
      await page.unroute(path);
      await page.getByRole('button',{name:'Retry now'}).click();
      await expect(brief).toBeVisible({timeout:20000});
      await expect(page.locator('body')).not.toContainText('Internal private failure');
    }
    await page.goto('/');
  }
});
