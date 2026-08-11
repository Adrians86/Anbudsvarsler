interface TrafficLightProps {
  tilbudsfrist?: string | null
  showLabel?: boolean
}

function getDaysUntil(fristStr?: string | null): number | null {
  if (!fristStr) return null
  try {
    const frist = new Date(fristStr.slice(0, 19))
    const now = new Date()
    return Math.floor((frist.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  } catch {
    return null
  }
}

export default function TrafficLight({ tilbudsfrist, showLabel = true }: TrafficLightProps) {
  const days = getDaysUntil(tilbudsfrist)

  if (days === null) {
    return (
      <span title="Ingen frist">
        ⚪{showLabel && <span className="ml-1 text-xs text-gray-400">Ingen frist</span>}
      </span>
    )
  }
  if (days < 0) {
    return (
      <span title="Frist utløpt">
        ⚫{showLabel && <span className="ml-1 text-xs text-gray-500">Utgått</span>}
      </span>
    )
  }
  if (days <= 7) {
    return (
      <span title={`${days} dager igjen`}>
        🔴{showLabel && <span className="ml-1 text-xs text-red-600">{days}d</span>}
      </span>
    )
  }
  if (days <= 21) {
    return (
      <span title={`${days} dager igjen`}>
        🟡{showLabel && <span className="ml-1 text-xs text-yellow-600">{days}d</span>}
      </span>
    )
  }
  return (
    <span title={`${days} dager igjen`}>
      🟢{showLabel && <span className="ml-1 text-xs text-green-600">{days}d</span>}
    </span>
  )
}

export { getDaysUntil }
