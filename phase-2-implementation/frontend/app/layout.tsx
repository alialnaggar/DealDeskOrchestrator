import type { Metadata } from 'next';
import Link from 'next/link';
import './style.css';
import './hardening.css';
import './light-theme.css';
export const metadata: Metadata = { title: 'Deal Desk | Supervisor', description: 'Offline, source-grounded deal intelligence demonstration' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body><a className="skip-link" href="#main-content">Skip to content</a><div className="shell"><header className="topbar"><Link href="/" className="brand"><span className="brandmark">DD</span><span>DEAL DESK <small>/ SUPERVISOR CONSOLE</small></span></Link><span className="environment">● LOCAL · OFFLINE SCRIPTED</span></header>{children}<footer>Decision support only · Synthetic fixture data · Human authority required</footer></div></body></html>; }
