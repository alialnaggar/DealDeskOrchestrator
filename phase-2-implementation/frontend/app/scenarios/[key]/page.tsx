import { notFound } from 'next/navigation';
import { ScenarioIntro } from '@/components/scenario-intro';
import { guides } from '@/lib/scenario-guide';
import { publicSyntheticDemo } from '@/lib/security';
import { sessionFromCookie, verifyIntakeReceipt } from '@/lib/security';
import { cookies } from 'next/headers';
export const dynamic = 'force-dynamic';
export default async function Scenario({params,searchParams}: {params: Promise<{key:string}>;searchParams:Promise<{intake?:string}>}) {
  const {key} = await params;
  if (key !== 'rc01' && key !== 'uc02') notFound();
  const query=await searchParams;
  const nonce=sessionFromCookie((await cookies()).get('dd_operator')?.value);
  const receipt=verifyIntakeReceipt(query.intake,nonce);
  return <ScenarioIntro scenario={key} guide={guides[key]} publicAccess={publicSyntheticDemo()} intake={receipt?.scenario===key ? {digest:receipt.digest,receipt:query.intake!} : null}/>;
}
