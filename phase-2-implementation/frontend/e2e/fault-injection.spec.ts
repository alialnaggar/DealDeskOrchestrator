import { test, expect } from '@playwright/test';
import { execFileSync, spawn, type ChildProcess } from 'node:child_process';
import { closeSync, openSync, readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';

// Opt-in only. Run with an exclusively owned fresh disposable fixture and no
// existing Python API on port 8765; this suite starts and stops its own server.
const file = process.env.D5_DISPOSABLE_ENV_FILE;
test.skip(!file, 'Requires D5_DISPOSABLE_ENV_FILE pointing to a fresh disposable API fixture');
const api = 'http://127.0.0.1:8765';
const ui = 'http://127.0.0.1:3000';
const py = '/tmp/opencode/dealdesk-test-venv/bin/python';
const backend = resolve(process.cwd(), '../backend');
let child: ChildProcess | undefined;
let fixture: Record<string,string>;
function loadFixture() {
  if (!file || !/^\/tmp\/opencode\/[A-Za-z0-9_-]+\.env$/.test(file) || (statSync(file).mode & 0o077) !== 0) throw new Error('Owner-only disposable environment file required');
  const rows = Object.fromEntries(readFileSync(file,'utf8').trim().split('\n').map(line => {
    const match = /^export ([A-Z0-9_]+)='([^']+)'$/.exec(line); if (!match) throw new Error('Invalid fixture environment'); return [match[1],match[2]];
  }));
  const business = rows.DEALDESK_DEMO_BUSINESS_DSN;
  const checkpoint = rows.DEALDESK_DEMO_CHECKPOINT_DSN;
  const name = business?.match(/\bdbname=(demo_api_[0-9a-f]{12})_business$/)?.[1];
  if (!name || !/^user=ubuntu host=\/tmp\/opencode port=55539 dbname=demo_api_[0-9a-f]{12}_business$/.test(business) || checkpoint !== `user=ubuntu host=/tmp/opencode port=55539 dbname=${name}_checkpoint` || rows.DEALDESK_PHASE1C_CHECKOUT !== '/tmp/opencode/dealdesk-phase1c-pinned') throw new Error('Only matched local disposable databases allowed');
  if (!process.env.DEALDESK_DEMO_TOKEN || !process.env.DEALDESK_UI_PASSWORD) throw new Error('Local operator test secrets required');
  return rows;
}
function fixturePython(code: string, ...args: string[]) {
  return execFileSync(py, ['-c', code, ...args], { env:{...process.env,PYTHONPATH:backend},timeout:30000,stdio:'pipe' }).toString().trim();
}
async function ready() {
  for(let i=0;i<120;i++) {
    try { if((await fetch(`${api}/demo/assessments/${'0'.repeat(32)}`)).status===401) return; } catch { /* starting */ }
    await new Promise(r=>setTimeout(r,100));
  }
  throw new Error('Test-owned Python API did not start');
}
async function start() {
  const env: NodeJS.ProcessEnv = {...process.env,...fixture,DEALDESK_DEMO_OWNER:'operator',DEALDESK_DEMO_TOKEN:process.env.DEALDESK_DEMO_TOKEN!,PYTHONPATH:backend};
  for(const name of Object.keys(env)) if (/^(GROQ|OPENAI|ANTHROPIC|TOGETHER)_/.test(name)) delete env[name];
  const fd = openSync('/tmp/opencode/d5-fault-api.log','a',0o600);
  child = spawn(py,['-m','dealdesk_phase2.assessment_api'],{env,stdio:['ignore',fd,fd]});
  closeSync(fd);
  await ready();
}
async function stop(signal: NodeJS.Signals) {
  const current = child;
  if (!current || current.exitCode !== null || current.signalCode !== null) return;
  await new Promise<void>(resolve => { current.once('exit',()=>resolve()); current.kill(signal); });
  child = undefined;
}
test.beforeAll(async () => {
  fixture = loadFixture();
  try { await fetch(`${api}/demo/assessments/${'0'.repeat(32)}`); throw new Error('Stop the existing API first; fault suite must own port 8765'); }
  catch(e) { if (e instanceof Error && e.message.startsWith('Stop the existing API')) throw e; }
  await start();
});
test.afterAll(async () => { await stop('SIGTERM'); });

test('real source drift, checkpoint corruption, storage outage and process interruption fail closed', async ({page}) => {
  test.setTimeout(240000);
  await page.goto('/');
  await page.getByLabel('Operator password').fill(process.env.DEALDESK_UI_PASSWORD!);
  await page.getByRole('button',{name:/Enter workspace/}).click();
  await page.getByRole('button',{name:'Run B01/RC01 offline assessment'}).click();
  await expect(page).toHaveURL(/\/assessments\/[0-9a-f]{32}/);
  const rc = page.url().split('/').at(-1)!;
  await expect(page.getByRole('heading',{name:'A supported schedule is not an accepted deal.'})).toBeVisible({timeout:120000});
  const events = await (await page.request.get(`${ui}/api/assessments/${rc}/events?after=0`)).json();
  expect(events.events).toHaveLength(21);

  // API process outage: an already displayed decision must disappear, not linger.
  await stop('SIGKILL');
  await expect(page.getByRole('alert').filter({hasText:'Local offline service unavailable'})).toBeVisible({timeout:15000});
  await expect(page.getByRole('heading',{name:'A supported schedule is not an accepted deal.'})).toHaveCount(0);
  expect((await page.request.get(`${ui}/api/assessments/${rc}/status`)).status()).toBe(502);
  await start();
  await expect(page.getByRole('heading',{name:'A supported schedule is not an accepted deal.'})).toBeVisible({timeout:15000});
  expect((await (await page.request.get(`${ui}/api/assessments/${rc}/events?after=0`)).json()).events).toEqual(events.events);
  console.log('D5 recovered RC01:',rc,'events:',events.events.length);

  // Only mutate the disposable B01 source; the old completed review must be withheld.
  const source = fixture.DEALDESK_DEMO_BUSINESS_DSN;
  const sourceSql = 'import sys,psycopg\nwith psycopg.connect(sys.argv[1]) as db:\n n=db.execute("UPDATE deal_desk.customer_credit_profiles SET credit_status=%s WHERE customer_id=%s AND credit_status=%s",(sys.argv[2],"M18-C-B01",sys.argv[3])).rowcount\n assert n==1,n';
  fixturePython(sourceSql, source, 'On-Hold', 'Active');
  try {
    await expect(page.getByRole('alert').filter({hasText:'Source evidence changed'})).toBeVisible({timeout:15000});
    await expect(page.getByRole('heading',{name:'A supported schedule is not an accepted deal.'})).toHaveCount(0);
    expect((await page.request.get(`${ui}/api/assessments/${rc}/status`)).status()).toBe(409);
    expect((await page.request.get(`${ui}/api/assessments/${rc}/review`)).status()).toBe(409);
  } finally { fixturePython(sourceSql, source, 'Active', 'On-Hold'); }
  await expect(page.getByRole('heading',{name:'A supported schedule is not an accepted deal.'})).toBeVisible({timeout:15000});

  // Disable *only new connections to this disposable checkpoint database*.
  const checkpoint = fixture.DEALDESK_DEMO_CHECKPOINT_DSN;
  const database = checkpoint.match(/\bdbname=(demo_api_[0-9a-f]{12}_checkpoint)$/)![1];
  const toggle = 'import sys,psycopg\nfrom psycopg import sql\nwith psycopg.connect("host=/tmp/opencode port=55539 user=ubuntu dbname=postgres",autocommit=True) as db:\n db.execute(sql.SQL("ALTER DATABASE {} ALLOW_CONNECTIONS "+sys.argv[2]).format(sql.Identifier(sys.argv[1])))';
  fixturePython(toggle, database, 'false');
  try {
    await expect(page.getByRole('alert').filter({hasText:'Local offline service unavailable'})).toBeVisible({timeout:15000});
    expect((await page.request.get(`${api}/demo/assessments/${rc}`,{headers:{Authorization:`Bearer ${process.env.DEALDESK_DEMO_TOKEN}`}})).status()).toBe(503);
  } finally { fixturePython(toggle, database, 'true'); }
  await expect(page.getByRole('heading',{name:'A supported schedule is not an accepted deal.'})).toBeVisible({timeout:15000});

  await page.goto('/'); await page.getByRole('button',{name:'Run N01/UC02 offline assessment'}).click();
  await expect(page).toHaveURL(/\/assessments\/[0-9a-f]{32}/);
  const uc = page.url().split('/').at(-1)!;
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toBeVisible({timeout:120000});
  const ucEvents = await (await page.request.get(`${ui}/api/assessments/${uc}/events?after=0`)).json();
  const tamper = 'import sys\nfrom pathlib import Path\nfrom dealdesk_phase2.assessment_service import AssessmentService\nfrom dealdesk_phase2.checkpoint import thesis_checkpointer\ns=AssessmentService(sys.argv[1],sys.argv[2],Path(sys.argv[3]))\nwith thesis_checkpointer(sys.argv[2]) as saver:\n g=s._graph(saver);config={"configurable":{"thread_id":sys.argv[4]}};ctx=dict(g.get_state(config).values["context"]);ctx["assessment_id"]="forged";g.update_state(config,{"context":ctx},as_node="finish")';
  fixturePython(tamper,source,checkpoint,fixture.DEALDESK_PHASE1C_CHECKOUT,uc);
  await expect(page.getByRole('alert').filter({hasText:'Source evidence changed'})).toBeVisible({timeout:15000});
  expect((await page.request.get(`${ui}/api/assessments/${uc}/review`)).status()).toBe(409);
  await stop('SIGTERM'); await start();
  expect((await page.request.get(`${ui}/api/assessments/${uc}/review`)).status()).toBe(409);
  expect((await page.request.get(`${api}/demo/assessments/${uc}/events`,{headers:{Authorization:`Bearer ${process.env.DEALDESK_DEMO_TOKEN}`}})).status()).toBe(409);
  const count = fixturePython('import sys,psycopg\nwith psycopg.connect(sys.argv[1]) as db:\n print(db.execute("SELECT count(*) FROM dealdesk_demo.assessment_events WHERE assessment_id=%s",(sys.argv[2],)).fetchone()[0])',checkpoint,uc);
  expect(Number(count)).toBe(ucEvents.events.length);
  console.log('D5 corrupted UC02 withheld:',uc,'events:',ucEvents.events.length);

  // Concurrent duplicate submissions must share an ID, including after restart.
  const csrf = await page.evaluate(async()=> (await (await fetch('/api/auth/csrf')).json()).csrf);
  const key = `d5-concurrent-${crypto.randomUUID()}`;
  const post = (scenario='N01/UC02') => page.request.post(`${ui}/api/assessments`,{data:{scenario},headers:{Origin:ui,'X-CSRF-Token':csrf,'Idempotency-Key':key}});
  const submitted = await Promise.all(Array.from({length:6},()=>post()));
  expect(submitted.map(r=>r.status())).toEqual([202,202,202,202,202,202]);
  const bodies=await Promise.all(submitted.map(r=>r.json()));
  expect(new Set(bodies.map(r=>r.assessment_id)).size).toBe(1);
  expect(bodies.filter(r=>r.created)).toHaveLength(1);
  expect((await post('B01/RC01')).status()).toBe(409);
  console.log('D5 concurrent duplicate ID:',bodies[0].assessment_id);

  // Kill a freshly accepted worker. Startup must mark it uncertain, not replay it.
  const freshKey = `d5-interrupt-${crypto.randomUUID()}`;
  const accepted = await page.request.post(`${ui}/api/assessments`,{data:{scenario:'B01/RC01'},headers:{Origin:ui,'X-CSRF-Token':csrf,'Idempotency-Key':freshKey}});
  expect(accepted.status()).toBe(202);
  const interrupted = (await accepted.json()).assessment_id;
  await stop('SIGKILL'); await start();
  const after = await page.request.get(`${ui}/api/assessments/${interrupted}/status`);
  expect(after.status()).toBe(200);
  expect((await after.json()).status).toBe('uncertain');
  expect((await page.request.get(`${ui}/api/assessments/${interrupted}/review`)).status()).toBe(409);
  const retry = await page.request.post(`${ui}/api/assessments`,{data:{scenario:'B01/RC01'},headers:{Origin:ui,'X-CSRF-Token':csrf,'Idempotency-Key':freshKey}});
  expect(retry.status()).toBe(202);
  expect(await retry.json()).toMatchObject({assessment_id:interrupted,created:false,status:'uncertain'});
  await stop('SIGTERM'); await start();
  expect((await (await page.request.get(`${ui}/api/assessments/${interrupted}/status`)).json()).status).toBe('uncertain');
  console.log('D5 interrupted run remained uncertain:',interrupted);
});
