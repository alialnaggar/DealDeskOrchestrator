// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
vi.mock('server-only', () => ({}));
import { BackendError, getStatus } from '../lib/backend';
const id = 'a'.repeat(32);
const valid = {version:'demo-api-v1',assessment_id:id,scenario:'N01/UC02',mode:'offline_scripted',status:'completed',last_sequence:20,phase1c_pin:'90c0bc8e'};
beforeEach(() => { process.env.DEALDESK_DEMO_TOKEN = 'local-operator-token-with-at-least-32-bytes'; });
afterEach(() => { vi.unstubAllGlobals(); delete process.env.DEALDESK_DEMO_TOKEN; delete process.env.DEALDESK_API_URL; });
describe('loopback-only server proxy', () => {
  it('passes bearer only to Python; rejects added fields without forwarding them', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok:true, json:async () => ({...valid, raw_checkpoint:'PRIVATE'}) });
    vi.stubGlobal('fetch', fetchMock);
    await expect(getStatus(id)).rejects.toMatchObject({status:502,message:'Upstream contract changed; review withheld'});
    const [url, request] = fetchMock.mock.calls[0];
    expect(url).toBe(`http://127.0.0.1:8765/demo/assessments/${id}`);
    expect(request.headers.Authorization).toBe('Bearer local-operator-token-with-at-least-32-bytes');
  });
  it('refuses a non-loopback backend even when configured', async () => {
    process.env.DEALDESK_API_URL = 'https://external.invalid';
    const fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock);
    await expect(getStatus(id)).rejects.toMatchObject({status:503});
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('does not reflect upstream error bodies, internal exception text or credentials', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ok:false,status:500,json:async()=>({detail:'private-dsn'})});
    vi.stubGlobal('fetch', fetchMock);
    await expect(getStatus(id)).rejects.toMatchObject({status:502,message:'Offline API unavailable'});
    fetchMock.mockRejectedValueOnce(new Error('database password=PRIVATE'));
    await expect(getStatus(id)).rejects.toBeInstanceOf(BackendError);
  });
});
