import type { VarslingStatus } from '@/lib/types'
import clsx from 'clsx'

const STATUS_STYLES: Record<VarslingStatus, string> = {
  NY: 'bg-gray-200 text-gray-700',
  SETT: 'bg-cyan-100 text-cyan-700',
  INTERESSERT: 'bg-navy text-white',
  FORKASTET: 'bg-red-100 text-red-700',
  LEVERT: 'bg-yellow-100 text-yellow-800',
  VUNNET: 'bg-green-100 text-green-700',
  TAPT: 'bg-gray-100 text-gray-500',
}

const STATUS_INLINE: Record<VarslingStatus, React.CSSProperties> = {
  INTERESSERT: { backgroundColor: '#1F3A5F', color: '#fff' },
  LEVERT: { backgroundColor: '#f0e6c8', color: '#7a5e1a' },
  NY: {},
  SETT: {},
  FORKASTET: {},
  VUNNET: {},
  TAPT: {},
}

interface StatusPillProps {
  status: VarslingStatus
  className?: string
}

export default function StatusPill({ status, className }: StatusPillProps) {
  return (
    <span
      className={clsx(
        'inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide',
        STATUS_STYLES[status],
        className
      )}
      style={STATUS_INLINE[status]}
    >
      {status}
    </span>
  )
}
