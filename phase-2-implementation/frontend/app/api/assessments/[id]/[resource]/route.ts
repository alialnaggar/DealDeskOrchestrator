import { NextRequest, NextResponse } from 'next/server';
import { assessmentId, BackendError, getEvents, getReview, getStatus } from '@/lib/backend';
import { denied, session } from '@/lib/security';
export const dynamic = 'force-dynamic';
export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string; resource: string }> }) {
  if (!session(request)) return denied();
  const { id, resource } = await params;
  if (!assessmentId.test(id) || !['status','events','review'].includes(resource)) return denied(404);
  const raw = request.nextUrl.searchParams.get('after') || '0';
  if (resource === 'events' && (!/^\d{1,15}$/.test(raw) || request.nextUrl.searchParams.size > 1)) return denied(400);
  try {
    const result = resource === 'status' ? await getStatus(id) : resource === 'events' ? await getEvents(id, Number(raw)) : await getReview(id);
    if (result.assessment_id !== id || (resource === 'events' && 'events' in result && result.events.some(e => e.assessment_id !== id))) throw new BackendError(502, 'Assessment identity mismatch');
    return NextResponse.json(result, { headers: { 'Cache-Control': 'no-store' } });
  } catch (err) { return NextResponse.json({ detail: err instanceof BackendError ? err.message : 'Offline API unavailable' }, { status: err instanceof BackendError ? err.status : 502, headers: { 'Cache-Control': 'no-store' } }); }
}
