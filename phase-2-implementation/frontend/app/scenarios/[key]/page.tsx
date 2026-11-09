import { notFound } from 'next/navigation';
import { ScenarioIntro } from '@/components/scenario-intro';
import { guides } from '@/lib/scenario-guide';
import { publicSyntheticDemo } from '@/lib/security';
export const dynamic = 'force-dynamic';
export default async function Scenario({params}: {params: Promise<{key:string}>}) {
  const {key} = await params;
  if (key !== 'rc01' && key !== 'uc02') notFound();
  return <ScenarioIntro scenario={key} guide={guides[key]} publicAccess={publicSyntheticDemo()} />;
}
