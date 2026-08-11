import type { Metadata } from 'next'
import './globals.css'
import Sidebar from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'Anbudsvarsler',
  description: 'Anbudsovervåking og tilbudsstøtte',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="no">
      <body className="flex min-h-screen" style={{ background: '#F4F6F9' }}>
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <div className="max-w-5xl mx-auto px-6 py-8">{children}</div>
        </main>
      </body>
    </html>
  )
}
