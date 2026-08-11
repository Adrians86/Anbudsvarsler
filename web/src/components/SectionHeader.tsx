interface SectionHeaderProps {
  eyebrow: string
  title: string
  subtitle?: string
}

export default function SectionHeader({ eyebrow, title, subtitle }: SectionHeaderProps) {
  return (
    <div className="mb-6">
      <p
        className="text-xs font-semibold uppercase tracking-widest mb-1"
        style={{ color: '#B08D2E' }}
      >
        {eyebrow}
      </p>
      <h1 className="text-2xl font-bold" style={{ color: '#1F3A5F' }}>
        {title}
      </h1>
      {subtitle && (
        <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
      )}
    </div>
  )
}
