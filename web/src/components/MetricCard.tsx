interface MetricCardProps {
  label: string
  value: string | number
  sub?: string
  icon?: string
}

export default function MetricCard({ label, value, sub, icon }: MetricCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      {icon && <div className="text-2xl mb-2">{icon}</div>}
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-bold" style={{ color: '#1F3A5F' }}>
        {value}
      </p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}
