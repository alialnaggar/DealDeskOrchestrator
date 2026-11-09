import { Landing } from '@/components/landing';
import { publicSyntheticDemo } from '@/lib/security';
export const dynamic = 'force-dynamic';
export default function Home() { return <Landing publicAccess={publicSyntheticDemo()} />; }
