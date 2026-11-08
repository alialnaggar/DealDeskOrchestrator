import { Workspace } from '@/components/workspace';
export default async function Assessment({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <Workspace id={id} />; }
