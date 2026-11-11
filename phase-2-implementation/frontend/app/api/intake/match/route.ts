import { NextRequest, NextResponse } from 'next/server';
import { DealInput } from '@/lib/intake-contract';
import { inputDigest, matchAuthoritativeFixture } from '@/lib/intake-server';
import { csrfOK, denied, issueIntakeReceipt, session } from '@/lib/security';
import { allowIntakeMatch } from '@/lib/intake-limit';

export async function POST(request:NextRequest) {
  const nonce=session(request); if(!nonce) return denied();
  if(!csrfOK(request,nonce) || request.headers.get('content-type')?.split(';')[0]!=='application/json') return denied(403);
  if(!allowIntakeMatch(nonce)) return NextResponse.json({detail:'Too many matching attempts. Retry later.'},{status:429,headers:{'Cache-Control':'no-store','Retry-After':'60'}});
  try {
    const reader=request.body?.getReader(); if(!reader) return denied(400);
    const chunks:Uint8Array[]=[]; let length=0;
    for (;;) { const {done,value}=await reader.read(); if(done) break; length+=value.byteLength; if(length>4096) { await reader.cancel(); return denied(413); } chunks.push(value); }
    const parsed=DealInput.safeParse(JSON.parse(new TextDecoder().decode(Buffer.concat(chunks))));
    if(!parsed.success) return NextResponse.json({detail:'Deal entry is invalid; review required fields and values.'},{status:400,headers:{'Cache-Control':'no-store'}});
    const match=matchAuthoritativeFixture(parsed.data);
    return NextResponse.json(match ? {matched:true,scenario:match,receipt:issueIntakeReceipt(nonce,match,inputDigest(parsed.data))} : {matched:false}, {headers:{'Cache-Control':'no-store'}});
  } catch { return NextResponse.json({detail:'Fixture validation unavailable. No assessment was started.'},{status:503,headers:{'Cache-Control':'no-store'}}); }
}
