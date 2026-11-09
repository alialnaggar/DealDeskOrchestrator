import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { Landing } from '../components/landing';
import { ScenarioIntro } from '../components/scenario-intro';
import { guides } from '../lib/scenario-guide';
import { ApiError } from '../components/client';
const push = vi.fn();
vi.mock('next/navigation', () => ({ useRouter: () => ({ push }) }));
vi.mock('../components/client', async original => {
  const actual = await original<typeof import('../components/client')>();
  return { ...actual, csrf: vi.fn(), json: vi.fn() };
});
import { csrf, json } from '../components/client';
afterEach(() => { cleanup(); vi.resetAllMocks(); sessionStorage.clear(); });
describe('guided synthetic scenario', () => {
  it('navigates to a pre-run brief without launching, and has no public password form', () => {
    render(<Landing publicAccess />);
    expect(screen.getByRole('heading',{name:'From request to responsible decision.'})).toBeTruthy();
    expect(screen.getByRole('heading',{name:'System Capabilities & Validation'})).toBeTruthy();
    expect(screen.getByRole('link',{name:'Explore Scenario B01/RC01'}).getAttribute('href')).toBe('/scenarios/rc01');
    expect(screen.getByRole('link',{name:'Explore Scenario N01/UC02'}).getAttribute('href')).toBe('/scenarios/uc02');
    expect(screen.queryByLabelText('Operator password')).toBeNull();
    expect(json).not.toHaveBeenCalled();
  });
  it('keeps the launch key after an ambiguous failure and never double-submits', async () => {
    vi.mocked(csrf).mockResolvedValue({ csrf:'a'.repeat(64),authenticated:true });
    let rejectFirst: (error: Error) => void = () => {};
    vi.mocked(json).mockImplementationOnce(() => new Promise((_, reject) => { rejectFirst = reject; }));
    render(<ScenarioIntro scenario="rc01" guide={guides.rc01} publicAccess />);
    const button = await screen.findByRole('button',{name:/Run Assessment/});
    await waitFor(() => expect(button).toHaveProperty('disabled',false));
    expect(screen.getByRole('heading',{name:'Structured deal record'})).toBeTruthy();
    expect(screen.getByRole('heading',{name:'Six specialists, one governed assessment'})).toBeTruthy();
    fireEvent.click(button); fireEvent.click(button);
    expect(json).toHaveBeenCalledTimes(1);
    const first = (vi.mocked(json).mock.calls[0][2] as RequestInit).headers as Record<string,string>;
    rejectFirst(new ApiError(502,'Unavailable'));
    await screen.findByText(/Retry will reuse the saved request key/);
    vi.mocked(json).mockResolvedValueOnce({ assessment_id:'a'.repeat(32),created:false });
    fireEvent.click(button);
    await waitFor(() => expect(push).toHaveBeenCalledWith('/assessments/'+'a'.repeat(32)));
    const second = (vi.mocked(json).mock.calls[1][2] as RequestInit).headers as Record<string,string>;
    expect(second['Idempotency-Key']).toBe(first['Idempotency-Key']);
    expect(sessionStorage.length).toBe(0);
  });
});
