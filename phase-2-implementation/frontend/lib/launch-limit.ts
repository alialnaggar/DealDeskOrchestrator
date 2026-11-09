// A bounded, process-local cap for the single-instance synthetic demo. No IP or
// client-supplied forwarding header is trusted; all anonymous sessions share a cap.
export function createLaunchLimiter() {
  const attempts: number[] = [];
  const created = new Map<string, { at: number; session: string }>();
  return (session: string, key: string, now = Date.now()) => {
    while (attempts.length && attempts[0] <= now - 60 * 60_000) attempts.shift();
    for (const [id, entry] of created) if (entry.at <= now - 60 * 60_000) created.delete(id);
    if (attempts.filter(at => at > now - 60_000).length >= 30 || attempts.length >= 120) return false;
    const id = `${session}:${key}`;
    if (!created.has(id)) {
      const entries = [...created.values()];
      if (entries.filter(entry => entry.at > now - 60_000).length >= 8 || entries.length >= 40 ||
          entries.filter(entry => entry.session === session && entry.at > now - 60_000).length >= 4 ||
          entries.filter(entry => entry.session === session).length >= 12) return false;
      created.set(id, { at: now, session });
    }
    attempts.push(now);
    return true;
  };
}
export const allowScenarioLaunch = createLaunchLimiter();
