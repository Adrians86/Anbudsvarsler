'use client'

import { useState, useEffect, useCallback } from 'react'
import SectionHeader from '@/components/SectionHeader'
import StatusPill from '@/components/StatusPill'
import TrafficLight, { getDaysUntil } from '@/components/TrafficLight'
import { fetchVarsler, updateVarslingStatus } from '@/lib/api'
import type { Varsling, VarslingStatus } from '@/lib/types'
import { useProfile } from '@/hooks/useProfile'

const ALL_STATUSER: VarslingStatus[] = [
  'NY', 'SETT', 'INTERESSERT', 'FORKASTET', 'LEVERT', 'VUNNET', 'TAPT',
]

const FILTER_STATUSER: VarslingStatus[] = ['NY', 'SETT', 'INTERESSERT', 'FORKASTET']

function formatNok(v: number | undefined | null): string {
  if (v == null) return ''
  return new Intl.NumberFormat('nb-NO', { maximumFractionDigits: 0 }).format(v) + ' NOK'
}

export default function FristerPage() {
  const { profilId, loaded } = useProfile()
  const [varsler, setVarsler] = useState<Varsling[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<Set<VarslingStatus>>(
    new Set<VarslingStatus>(['NY', 'SETT', 'INTERESSERT'])
  )
  const [pendingStatus, setPendingStatus] = useState<Record<number, VarslingStatus>>({})
  const [savingId, setSavingId] = useState<number | null>(null)

  const loadData = useCallback(async () => {
    if (!profilId) return
    setLoading(true)
    setError(null)
    try {
      const v = await fetchVarsler(profilId)
      setVarsler(v)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ukjent feil')
    } finally {
      setLoading(false)
    }
  }, [profilId])

  useEffect(() => {
    if (loaded && profilId) loadData()
  }, [loaded, profilId, loadData])

  function toggleStatusFilter(s: VarslingStatus) {
    setStatusFilter((prev) => {
      const next = new Set(prev)
      if (next.has(s)) next.delete(s)
      else next.add(s)
      return next
    })
  }

  async function handleSaveStatus(varslingId: number) {
    const ny = pendingStatus[varslingId]
    if (!ny) return
    setSavingId(varslingId)
    try {
      await updateVarslingStatus(varslingId, ny)
      setVarsler((prev) =>
        prev.map((v) => (v.id === varslingId ? { ...v, status: ny } : v))
      )
      setPendingStatus((p) => {
        const next = { ...p }
        delete next[varslingId]
        return next
      })
    } catch (e) {
      alert(`Feil: ${e instanceof Error ? e.message : e}`)
    } finally {
      setSavingId(null)
    }
  }

  if (!loaded) return null

  if (!profilId) {
    return (
      <div>
        <SectionHeader eyebrow="FRISTMONITOR" title="⏰ Fristmonitor" />
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg p-4 text-sm">
          Ingen profil valgt. Sett profil_id i sessionStorage.
        </div>
      </div>
    )
  }

  // Banner warnings for INTERESSERT varsler
  const bannerVarsler = varsler.filter(
    (v) => v.status === 'INTERESSERT' && v.tilbudsfrist
  )

  const withFrist = varsler.filter((v) => v.tilbudsfrist)
  const snart = withFrist.filter((v) => {
    const d = getDaysUntil(v.tilbudsfrist)
    return d !== null && d >= 0 && d <= 21
  })

  // Sort: nearest deadline first, then no deadline
  const filtered = varsler
    .filter((v) => statusFilter.size === 0 || statusFilter.has(v.status))
    .sort((a, b) => {
      const da = a.tilbudsfrist ?? '9999-12-31'
      const db = b.tilbudsfrist ?? '9999-12-31'
      return da.localeCompare(db)
    })

  return (
    <div>
      <SectionHeader eyebrow="FRISTMONITOR" title="⏰ Fristmonitor" />

      {/* Banner warnings */}
      {bannerVarsler
        .sort((a, b) => (getDaysUntil(a.tilbudsfrist) ?? 9999) - (getDaysUntil(b.tilbudsfrist) ?? 9999))
        .map((v) => {
          const days = getDaysUntil(v.tilbudsfrist)
          if (days == null || days < 0) return null
          const tittel = v.tittel ?? 'Ukjent anbud'
          if (days <= 1) {
            return (
              <div key={v.id} className="mb-2 bg-red-600 text-white rounded-lg px-4 py-3 text-sm font-semibold">
                SISTE SJANSE — {days} dag igjen: {tittel}
              </div>
            )
          }
          if (days <= 3) {
            return (
              <div key={v.id} className="mb-2 bg-red-50 border border-red-300 text-red-700 rounded-lg px-4 py-3 text-sm">
                🔴 <strong>3 dager eller mindre:</strong> {tittel} ({days} dager igjen)
              </div>
            )
          }
          if (days <= 7) {
            return (
              <div key={v.id} className="mb-2 bg-orange-50 border border-orange-300 text-orange-700 rounded-lg px-4 py-3 text-sm">
                🟠 <strong>7 dager til frist:</strong> {tittel} ({days} dager igjen)
              </div>
            )
          }
          if (days <= 14) {
            return (
              <div key={v.id} className="mb-2 bg-blue-50 border border-blue-300 text-blue-700 rounded-lg px-4 py-3 text-sm">
                🔵 <strong>14 dager til frist:</strong> {tittel} ({days} dager igjen)
              </div>
            )
          }
          return null
        })}

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6 mt-4">
        {[
          { label: 'Totalt aktive', value: varsler.length },
          { label: 'Med tilbudsfrist', value: withFrist.length },
          { label: 'Frister innen 3 uker', value: snart.length },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 text-center"
          >
            <p className="text-2xl font-bold" style={{ color: '#1F3A5F' }}>
              {value}
            </p>
            <p className="text-xs text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Status filter */}
      <div className="flex flex-wrap gap-2 mb-4">
        {FILTER_STATUSER.map((s) => (
          <button
            key={s}
            onClick={() => toggleStatusFilter(s)}
            className="px-3 py-1 rounded-full text-xs font-semibold border transition-colors"
            style={
              statusFilter.has(s)
                ? { background: '#1F3A5F', color: '#fff', borderColor: '#1F3A5F' }
                : { background: '#fff', color: '#555', borderColor: '#d1d5db' }
            }
          >
            {s}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-sm text-gray-500 animate-pulse">Laster frister...</div>
      ) : filtered.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 text-gray-500 rounded-lg p-4 text-sm">
          Ingen varslinger å vise med valgte filtre.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((v) => {
            const currentStatus = pendingStatus[v.id] ?? v.status
            const days = getDaysUntil(v.tilbudsfrist)

            return (
              <div
                key={v.id}
                className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex gap-4"
              >
                {/* Traffic light */}
                <div className="text-center shrink-0 pt-1" style={{ minWidth: 64 }}>
                  <TrafficLight tilbudsfrist={v.tilbudsfrist} showLabel={false} />
                  {v.tilbudsfrist ? (
                    <p className="text-xs text-gray-500 mt-1">
                      {days != null && days >= 0 ? `${days}d` : 'Utgått'}
                    </p>
                  ) : (
                    <p className="text-xs text-gray-400 mt-1">Ingen frist</p>
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 text-sm truncate">
                    {v.tittel ?? `Varsling #${v.id}`}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {v.oppdragsgiver ?? ''}
                  </p>
                  {v.tilbudsfrist && (
                    <p className="text-xs text-gray-400 mt-1">
                      Frist: {v.tilbudsfrist.slice(0, 10)}
                    </p>
                  )}
                  {v.cpv_koder?.length ? (
                    <p className="text-xs text-gray-400 mt-0.5">
                      CPV: {v.cpv_koder.slice(0, 3).join(', ')}
                    </p>
                  ) : null}
                </div>

                {/* Meta */}
                <div className="flex flex-col items-end gap-1.5 shrink-0">
                  <StatusPill status={v.status} />
                  <span className="text-xs font-medium" style={{ color: '#1F3A5F' }}>
                    {(v.relevans_score * 100).toFixed(0)}% relevans
                  </span>
                  {v.estimert_verdi && (
                    <span className="text-xs text-gray-500">{formatNok(v.estimert_verdi)}</span>
                  )}
                  {v.url && (
                    <a
                      href={v.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs underline"
                      style={{ color: '#1F3A5F' }}
                    >
                      Åpne
                    </a>
                  )}

                  {/* Status update */}
                  <div className="flex gap-1 items-center mt-1">
                    <select
                      className="border border-gray-200 rounded px-2 py-1 text-xs bg-white"
                      value={currentStatus}
                      onChange={(e) =>
                        setPendingStatus((p) => ({
                          ...p,
                          [v.id]: e.target.value as VarslingStatus,
                        }))
                      }
                    >
                      {ALL_STATUSER.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                    {currentStatus !== v.status && (
                      <button
                        onClick={() => handleSaveStatus(v.id)}
                        disabled={savingId === v.id}
                        className="px-2 py-1 rounded text-xs font-medium text-white disabled:opacity-40"
                        style={{ background: '#1F3A5F' }}
                      >
                        {savingId === v.id ? '...' : 'Lagre'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
