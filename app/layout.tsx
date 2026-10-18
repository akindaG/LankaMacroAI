import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = { title: 'LankaMacro AI · Economic research', description: 'Explore Sri Lankan economic evidence, source-backed inflation charts and transparent scenarios.' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
