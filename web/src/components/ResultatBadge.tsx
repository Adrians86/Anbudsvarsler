import type { KvalResultat } from '@/lib/types'
import clsx from 'clsx'

const RESULTAT_STYLES: Record<KvalResultat, { bg: string; text: string; label: string }> = {
  GO: { bg: '#2ECC71', text: '#fff', label: 'GO' },
  'NO-GO': { bg: '#C0392B', text: '#fff', label: 'NO-GO' },
  'GÅ VIDERE MED FORBEHOLD': { bg: '#E67E22', text: '#fff', label: 'GÅ VIDERE MED FORBEHOLD' },
}

interface ResultatBadgeProps {
  resultat: KvalResultat
  className?: string
}

export default function ResultatBadge({ resultat, className }: ResultatBadgeProps) {
  const s = RESULTAT_STYLES[resultat]
  return (
    <span
      className={clsx(
        'inline-block px-3 py-1 rounded text-xs font-bold uppercase tracking-wide',
        className
      )}
      style={{ backgroundColor: s.bg, color: s.text }}
    >
      {s.label}
    </span>
  )
}
