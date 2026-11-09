import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { ApiError } from '../components/client';
import { Workspace } from '../components/workspace';
const id = 'a'.repeat(32);
vi.mock('next/link',()=>({ default: ({children,href}:{children:React.ReactNode,href:string})=><a href={href}>{children}</a> }));
vi.mock('../components/client', async importOriginal => {
  const actual = await importOriginal<typeof import('../components/client')>();
  return { ...actual, status: vi.fn(), events: vi.fn(), review: vi.fn() };
});
import { status, events, review } from '../components/client';
import { Review } from '../lib/contracts';
import { sample } from './fixture';
afterEach(cleanup);
describe('failure-state UI', () => {
  it('shows loading while the offline API has not returned', () => {
    vi.mocked(status).mockReturnValue(new Promise(()=>{}));
    render(<Workspace id={id}/>);
    expect(screen.getByRole('status').textContent).toContain('Loading persisted status');
  });
  it('shows a stopped run without inventing an outcome or a review', async () => {
    vi.mocked(status).mockResolvedValue({ version:'demo-api-v1',assessment_id:id,scenario:'N01/UC02',mode:'offline_scripted',status:'stopped',last_sequence:1,phase1c_pin:'pin' });
    vi.mocked(events).mockResolvedValue([{assessment_id:id,sequence:1,occurred_at:'2026-11-08T12:00:00Z',kind:'stopped',stage:null}]);
    render(<Workspace id={id}/>);
    expect(await screen.findByText(/Execution stopped. No automatic replay/)).toBeTruthy();
    expect(screen.queryByText('No verified candidate')).toBeNull();
  });
  it('keeps an uncertain run and an empty event history separate from a validated review', async () => {
    vi.mocked(status).mockResolvedValue({ version:'demo-api-v1',assessment_id:id,scenario:'N01/UC02',mode:'offline_scripted',status:'uncertain',last_sequence:0,phase1c_pin:'pin' });
    vi.mocked(events).mockResolvedValue([]);
    render(<Workspace id={id}/>);
    expect(await screen.findByText(/Execution uncertain. No automatic replay/)).toBeTruthy();
    expect(screen.getByText('Not yet available')).toBeTruthy();
    expect(screen.queryByText('No verified candidate')).toBeNull();
  });
  it('withholds stale-source results on 409', async () => {
    vi.mocked(status).mockRejectedValue(new ApiError(409,'Source changed'));
    render(<Workspace id={'b'.repeat(32)}/>);
    expect(await screen.findByText(/Source evidence changed or review is unavailable/)).toBeTruthy();
  });
  it.each([
    [401, 'Operator session expired'],
    [403, 'Access refused'],
    [404, 'Assessment not found'],
    [502, 'Local offline service unavailable']
  ])('presents a safe %i response without showing the old decision', async (code, message) => {
    vi.mocked(status).mockRejectedValue(new ApiError(code,'PRIVATE-DSN-DO-NOT-ECHO'));
    const {container} = render(<Workspace id={id}/>);
    expect(await screen.findByRole('alert')).toHaveProperty('textContent', expect.stringContaining(message));
    expect(container.textContent).not.toContain('PRIVATE-DSN-DO-NOT-ECHO');
    expect(screen.queryByText('Six specialist responsibilities')).toBeNull();
  });
  it('shows completed review only after matching validated status and events', async () => {
    vi.mocked(status).mockResolvedValue({ version:'demo-api-v1',assessment_id:id,scenario:'N01/UC02',mode:'offline_scripted',status:'completed',last_sequence:1,phase1c_pin:'90c0bc8e' });
    vi.mocked(events).mockResolvedValue([{assessment_id:id,sequence:1,occurred_at:'2026-11-08T12:00:00Z',kind:'review_ready',stage:'review'}]);
    vi.mocked(review).mockResolvedValue(Review.parse(sample));
    render(<Workspace id={id}/>);
    expect(await screen.findByText('No verified candidate')).toBeTruthy();
    expect(screen.getByRole('heading',{name:'Review, not authorization'})).toBeTruthy();
  });
  it('hides a completed decision during a polling outage, then restores it', async () => {
    const valid = { version:'demo-api-v1' as const,assessment_id:id,scenario:'N01/UC02' as const,mode:'offline_scripted' as const,status:'completed' as const,last_sequence:1,phase1c_pin:'90c0bc8e' };
    vi.mocked(status).mockResolvedValueOnce(valid).mockRejectedValueOnce(new ApiError(502,'PRIVATE-DSN-DO-NOT-ECHO')).mockResolvedValue(valid);
    vi.mocked(events).mockResolvedValueOnce([{assessment_id:id,sequence:1,occurred_at:'2026-11-08T12:00:00Z',kind:'review_ready',stage:'review'}]).mockResolvedValue([]);
    vi.mocked(review).mockResolvedValue(Review.parse(sample));
    const {container} = render(<Workspace id={id}/>);
    expect(await screen.findByText('No verified candidate')).toBeTruthy();
    expect(await screen.findByRole('alert',{}, {timeout:4000})).toHaveProperty('textContent',expect.stringContaining('Retrying; review withheld'));
    expect(container.textContent).not.toContain('PRIVATE-DSN-DO-NOT-ECHO');
    expect(screen.queryByText('No verified candidate')).toBeNull();
    expect(await screen.findByText('No verified candidate',{}, {timeout:4000})).toBeTruthy();
  }, 10000);
});
