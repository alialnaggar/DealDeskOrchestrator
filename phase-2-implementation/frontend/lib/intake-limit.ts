// Separate, process-local match cap. Does not consume assessment launch quota.
export function createIntakeLimiter() {
  const attempts:number[]=[]; const sessions=new Map<string,number[]>();
  return (nonce:string,now=Date.now()) => {
    while(attempts.length && attempts[0]<=now-60_000) attempts.shift();
    const own=(sessions.get(nonce)||[]).filter(time=>time>now-60_000);
    if(attempts.length>=120 || own.length>=20) return false;
    attempts.push(now);own.push(now);sessions.set(nonce,own);
    for(const [session,times] of sessions) if(times.at(-1)!<=now-60_000) sessions.delete(session);
    return true;
  };
}
export const allowIntakeMatch=createIntakeLimiter();
