import { Workspace } from '@/components/workspace';
import { cookies } from 'next/headers';
import { sessionFromCookie, verifyIntakeReceipt } from '@/lib/security';
export default async function Assessment({ params, searchParams }: { params: Promise<{ id: string }>;searchParams:Promise<{intake?:string}> }) {
  const { id } = await params;const query=await searchParams;
  const nonce=sessionFromCookie((await cookies()).get('dd_operator')?.value);
  const intake=verifyIntakeReceipt(query.intake,nonce);
  return <Workspace key={id} id={id} intake={intake}/>;
}
