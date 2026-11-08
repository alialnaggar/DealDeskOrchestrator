import 'server-only';
import { Created, Events, Review, Status } from './contracts';
import { z } from 'zod';

export class BackendError extends Error { constructor(public status: number, message: string) { super(message); } }
export const assessmentId = /^[0-9a-f]{32}$/;
export async function backend<T>(path: string, schema: z.ZodType<T>, post?: { scenario: string; key: string }): Promise<T> {
  const token = process.env.DEALDESK_DEMO_TOKEN;
  const base = process.env.DEALDESK_API_URL || 'http://127.0.0.1:8765';
  if (!token || token.length < 32 || base !== 'http://127.0.0.1:8765') throw new BackendError(503, 'Local offline API configuration unavailable');
  try {
    const response = await fetch(base + path, { method: post ? 'POST' : 'GET', headers: { Authorization: `Bearer ${token}`, ...(post ? { 'Content-Type': 'application/json', 'Idempotency-Key': post.key } : {}) }, body: post ? JSON.stringify({ scenario: post.scenario }) : undefined, cache: 'no-store', signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new BackendError(response.status === 409 ? 409 : response.status === 404 ? 404 : 502, response.status === 409 ? 'Review not ready or source evidence changed' : response.status === 404 ? 'Assessment unavailable' : 'Offline API unavailable');
    const value = schema.safeParse(await response.json());
    if (!value.success) throw new BackendError(502, 'Upstream contract changed; review withheld');
    return value.data;
  } catch (err) { if (err instanceof BackendError) throw err; throw new BackendError(502, 'Offline API unavailable'); }
}
export const create = (scenario: string, key: string) => backend('/demo/assessments', Created, { scenario, key });
export const getStatus = (id: string) => backend(`/demo/assessments/${id}`, Status);
export const getEvents = (id: string, after: number) => backend(`/demo/assessments/${id}/events?after=${after}`, Events);
export const getReview = (id: string) => backend(`/demo/assessments/${id}/review`, Review);
