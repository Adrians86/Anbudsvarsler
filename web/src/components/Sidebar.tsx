'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

const navItems = [
  { href: '/', label: 'Hjem', icon: '🏠' },
  { href: '/varsler', label: 'Mine Varsler', icon: '🔔' },
  { href: '/sok', label: 'Søk', icon: '🔍' },
  { href: '/kvalifikasjon', label: 'Kvalifikasjon', icon: '✅' },
  { href: '/tilbud', label: 'Tilbud', icon: '📋' },
  { href: '/bibliotek', label: 'Bibliotek', icon: '📚' },
  { href: '/frister', label: 'Frister', icon: '⏰' },
  { href: '/innsikt', label: 'Innsikt', icon: '📊' },
  { href: '/admin', label: 'Admin', icon: '⚙️' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside
      style={{ width: 240, minWidth: 240, background: '#162d4e' }}
      className="flex flex-col h-screen sticky top-0 shrink-0"
    >
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/10">
        <span className="text-lg font-bold tracking-wide" style={{ color: '#B08D2E' }}>
          Anbudsvarsler
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {navItems.map(({ href, label, icon }) => {
          const isActive =
            href === '/' ? pathname === '/' : pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-3 px-5 py-3 text-sm font-medium transition-colors',
                isActive
                  ? 'border-l-4 text-white'
                  : 'border-l-4 border-transparent text-white/60 hover:text-white/90 hover:bg-white/5'
              )}
              style={
                isActive
                  ? { borderLeftColor: '#B08D2E', background: 'rgba(176,141,46,0.12)' }
                  : {}
              }
            >
              <span className="text-base">{icon}</span>
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 text-xs text-white/30 border-t border-white/10">
        MVP v0.1.0
      </div>
    </aside>
  )
}
