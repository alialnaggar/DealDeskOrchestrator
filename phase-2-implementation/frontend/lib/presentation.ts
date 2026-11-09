import type { EventDTO, StatusDTO } from './contracts';

// Execution is never synonymous with a favorable business result.
export const assessmentTone: Record<StatusDTO['status'], 'neutral' | 'info' | 'caution'> = {
  accepted: 'info', running: 'info', completed: 'neutral', stopped: 'caution', uncertain: 'caution'
};
export const assessmentLabel: Record<StatusDTO['status'], string> = {
  accepted: 'Queued · not assessed', running: 'Checks running', completed: 'Checks complete · review required',
  stopped: 'Stopped · review required', uncertain: 'Outcome uncertain · review required'
};
export const stageLabel: Record<EventDTO['kind'], string> = {
  accepted: 'Run queued', running: 'Run started', preflight_ok: 'Source preflight complete',
  checkpoint: 'Checkpoint stored', fixed_completed: 'Deterministic check recorded',
  ai_completed: 'Offline-scripted stage recorded', review_ready: 'Review available',
  stopped: 'Run stopped', uncertain: 'Run uncertain'
};
export function findingTone(value: string): 'neutral' | 'info' | 'caution' {
  if (value === 'unknown' || value === 'evidence_needed' || value === 'abstained' || value === 'blocked' || value === 'needs_revision') return 'caution';
  if (value === 'completed' || value === 'no_issue_identified') return 'neutral';
  return 'info';
}
