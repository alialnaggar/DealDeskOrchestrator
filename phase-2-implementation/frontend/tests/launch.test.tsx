import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { Landing } from '../components/landing';
import { ApiError } from '../components/client';
const push = vi.fn();
vi.mock('next/navigation', () => ({ useRouter: () => ({ push }) }));
vi.mock('../components/client', async original => {
  const actual = await original<typeof import('../components/client')>();
  return { ...actual, csrf: vi.fn(), json: vi.fn() };
});
import { csrf, json } from '../components/client';
afterEach(() => { cleanup(); vi.resetAllMocks(); sessionStorage.clear(); });
describe('scenario launch idempotency', () => {
  it('shows the intended architecture and both public synthetic choices without a password form', async () => {
    vi.mocked(csrf).mockResolvedValue({ csrf:'a'.repeat(64),authenticated:true });
    render(<Landing publicAccess />);
    expect(screen.getByRole('heading',{name:'Intelligent deal assessment.'})).toBeTruthy();
    expect(screen.getByText('Multi-Agent Orchestrator')).toBeTruthy();
    expect(screen.getByText('Human Decision')).toBeTruthy();
    expect(screen.getByText(/not six independent live AI calls/)).toBeTruthy();
    expect(screen.queryByLabelText('Operator password')).toBeNull();
    expect(await screen.findByRole('button',{name:'Run B01/RC01 offline assessment'})).toHaveProperty('disabled',false);
    expect(screen.getByRole('button',{name:'Run N01/UC02 offline assessment'})).toBeTruthy();
  });
  it('does not double-submit rapid clicks and reuses the key after a lost response', async () => {
    vi.mocked(csrf).mockResolvedValue({ csrf: 'a'.repeat(64), authenticated: true });
    let rejectFirst: (error: Error) => void = () => {};
    vi.mocked(json).mockImplementationOnce(() => new Promise((_, reject) => { rejectFirst = reject; }));
    render(<Landing/>);
    const button = await screen.findByRole('button',{name:'Run B01/RC01 offline assessment'});
    fireEvent.click(button); fireEvent.click(button);
    expect(json).toHaveBeenCalledTimes(1);
    const firstKey = (vi.mocked(json).mock.calls[0][2] as RequestInit).headers as Record<string,string>;
    rejectFirst(new ApiError(502,'Offline API unavailable'));
    await screen.findByText(/Retry will reuse the same request key/);
    vi.mocked(json).mockResolvedValueOnce({ assessment_id:'a'.repeat(32), created:false });
    fireEvent.click(button);
    await waitFor(() => expect(push).toHaveBeenCalledWith('/assessments/'+'a'.repeat(32)));
    const secondKey = (vi.mocked(json).mock.calls[1][2] as RequestInit).headers as Record<string,string>;
    expect(secondKey['Idempotency-Key']).toBe(firstKey['Idempotency-Key']);
    expect(sessionStorage.length).toBe(0);
  });
});
