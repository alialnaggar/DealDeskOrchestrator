import { Created, Events, Review, Status, type EventDTO, type StatusDTO } from '@/lib/contracts';
import { z } from 'zod';
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export async function json<T>(url: string, schema: z.ZodType<T>, init?: RequestInit) {
  const response = await fetch(url, { ...init, credentials: 'same-origin', cache: 'no-store' });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new ApiError(response.status, typeof body.detail === 'string' ? body.detail : 'Request failed'); }
  return schema.parse(await response.json());
}
export const status = (id: string) => json(`/api/assessments/${id}/status`, Status);
export const review = (id: string) => json(`/api/assessments/${id}/review`, Review);
export async function events(id: string, last = 0): Promise<EventDTO[]> {
  const items: EventDTO[] = []; let after = last;
  for (let page = 0; page < 100; page++) {
    const result = await json(`/api/assessments/${id}/events?after=${after}`, Events);
    if (result.assessment_id !== id || result.events.some(row => row.assessment_id !== id || row.sequence <= after || row.sequence > after + 100) || result.events.some((row, i) => i > 0 && row.sequence <= result.events[i - 1].sequence)) throw new Error('Invalid event cursor or assessment identity');
    items.push(...result.events);
    if (result.events.length < 100) return items;
    after = result.events.at(-1)!.sequence;
  }
  throw new Error('Event history exceeded safe pagination limit');
}
export function matchStatus(value: StatusDTO, id: string) { if (value.assessment_id !== id) throw new Error('Assessment identity mismatch'); return value; }
export async function csrf() { const res = await fetch('/api/auth/csrf', { cache: 'no-store' }); if (!res.ok) throw new Error('Session unavailable'); return res.json() as Promise<{ csrf: string; authenticated: boolean }>; }
export { Created };
