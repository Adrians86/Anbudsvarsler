'use client'

import { useState, useEffect, useCallback } from 'react'
import SectionHeader from '@/components/SectionHeader'
import { fetchKunngjøringer, fetchVarsler, fetchKvalifikasjoner } from '@/lib/api'
import type { Kunngjoring, Varsling, Kvalifikasjonssjekk } from '@/lib/types'
import { useProfile } from '@/hooks/useProfile'
import { getDaysUntil } from '@/components/TrafficLight'

const ALLE_STATUSER = ['NY', 'SETT', 'INTERESSERT', 'FORKASTET', 'LEVERT', 'VUNNET', 'TAPT']

const STATUS_COLORS: Record<string, string> = {
  NY: '#9CA3AF',
  SETT: '#06B6D4',
  INTERESSERT: '#1F3A5F',
  FORKASTET: '#EF4444',
  LEVERT: '#B08D2E',
  VUNNET: '#22C55E',
  TAPT: '#6B7280',
}

function SimpleBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? (value / max) * 100 : 0
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-600 w-24 shrink-0 text-right">{label}</span>
      <div className="flex-1 h-5 bg-gray-100 rounded overflow-hidden">
        <div
          className="h-full rounded transition-all"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="text-xs text-gray-500 w-6 shrink-0">{value}</span>
    </div>
  )
}

export default function InnsiktPage() {
  const { profilId, loaded } = useProfile()
  const [kunngjøringer, setKunngjøringer] = useState<Kunngjoring[]>([])
  const [varsler, setVarsler] = useState<Varsling[]>([])
  const [kvalifikasjoner, setKvalifikasjoner] = useState<Kvalifikasjonssjekk[]>([])
  const [loading, setLoading] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const k = await fetchKunngjøringer()
      setKunngjøringer(k)
      if (profilId) {
        const [v, kv] = await Promise.all([
          fetchVarsler(profilId),
          fetchKvalifikasjoner({ profilId }),
        ])
        setVarsler(v)
        setKvalifikasjoner(kv)
      }
    } catch {
      // graceful
    } finally {
      setLoading(false)
    }
  }, [profilId])

  useEffect(() => {
    if (loaded) loadData()
  }, [loaded, loadData])

  // Metrics
  const snittScore =
    varsler.length > 0
      ? varsler.reduce((sum, v) => sum + v.relevans_score, 0) / varsler.length
      : null

  const goCount = kvalifikasjoner.filter((k) => k.resultat === 'GO').length
  const gvCount = kvalifikasjoner.filter((k) => k.resultat === 'GÅ VIDERE MED FORBEHOLD').length
  const nogoCount = kvalifikasjoner.filter((k) => k.resultat === 'NO-GO').length
  const kvaliStr = kvalifikasjoner.length > 0 ? `GO:${goCount} / GV:${gvCount} / NO-GO:${nogoCount}` : '—'

  // Status distribution
  const statusTeller: Record<string, number> = {}
  ALLE_STATUSER.forEach((s) => { statusTeller[s] = 0 })
  varsler.forEach((v) => { statusTeller[v.status] = (statusTeller[v.status] ?? 0) + 1 })
  const maxStatus = Math.max(...Object.values(statusTeller), 1)

  // Relevans buckets
  const buckets: Record<string, number> = { '0–25 %': 0, '25–50 %': 0, '50–75 %': 0, '75–100 %': 0 }
  varsler.forEach((v) => {
    const s = v.relevans_score
    if (s < 0.25) buckets['0–25 %']++
    else if (s < 0.5) buckets['25–50 %']++
    else if (s < 0.75) buckets['50–75 %']++
    else buckets['75–100 %']++
  })
  const maxBucket = Math.max(...Object.values(buckets), 1)

  // Upcoming (30 days)
  const kommende = varsler
    .filter((v) => {
      const d = getDaysUntil(v.tilbudsfrist)
      return d !== null && d >= 0 && d <= 30
    })
    .sort((a, b) => (a.tilbudsfrist ?? '').localeCompare(b.tilbudsfrist ?? ''))

  // Kilde distribution
  const kildeTeller: Record<string, number> = {}
  kunngjøringer.forEach((k) => {
    kildeTeller[k.kilde] = (kildeTeller[k.kilde] ?? 0) + 1
  })
  const maxKilde = Math.max(...Object.values(kildeTeller), 1)

  return (
    <div>
      <SectionHeader eyebrow="INNSIKT" title="📊 Innsikt og statistikk" />

      {loading && <div className="text-sm text-gray-500 animate-pulse mb-4">Laster data...</div>}

      {/* Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Kunngjøringer i DB', value: kunngjøringer.length },
          {
            label: 'Aktive varsler',
            value: profilId ? varsler.length : '—',
          },
          {
            label: 'Gj.snitt relevans',
            value: snittScore !== null ? `${(snittScore * 100).toFixed(0)}%` : '—',
          },
          { label: 'GO / GV / NO-GO', value: kvaliStr },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="bg-white rounded-xl border border-gray-200 shadow-sm p-4"
          >
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
            <p className="text-xl font-bold" style={{ color: '#1F3A5F' }}>
              {value}
            </p>
          </div>
        ))}
      </div>

      {!profilId && (
        <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-700 rounded-lg p-4 text-sm">
          For profilspesifikk statistikk, sett en leverandørprofil (profil_id i sessionStorage).
        </div>
      )}

      {/* Status distribution */}
      {varsler.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <h2 className="text-sm font-semibold mb-4" style={{ color: '#1F3A5F' }}>
            Status-fordeling
          </h2>
          <div className="space-y-2">
            {ALLE_STATUSER.map((s) => (
              <SimpleBar
                key={s}
                label={s}
                value={statusTeller[s] ?? 0}
                max={maxStatus}
                color={STATUS_COLORS[s] ?? '#9CA3AF'}
              />
            ))}
          </div>
        </div>
      )}

      {/* Relevans buckets */}
      {varsler.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <h2 className="text-sm font-semibold mb-4" style={{ color: '#1F3A5F' }}>
            Relevans-fordeling
          </h2>
          <div className="space-y-2">
            {Object.entries(buckets).map(([label, value]) => (
              <SimpleBar
                key={label}
                label={label}
                value={value}
                max={maxBucket}
                color="#1F3A5F"
              />
            ))}
          </div>
        </div>
      )}

      {/* Upcoming deadlines */}
      {kommende.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <h2 className="text-sm font-semibold mb-4" style={{ color: '#1F3A5F' }}>
            Frister de neste 30 dagene
          </h2>
          <div className="space-y-2">
            {kommende.map((v) => {
              const days = getDaysUntil(v.tilbudsfrist) ?? 0
              const lys = days <= 7 ? '🔴' : days <= 21 ? '🟡' : '🟢'
              return (
                <div key={v.id} className="flex items-center gap-3 text-sm">
                  <span className="text-base">{lys}</span>
                  <span className="flex-1 truncate font-medium">
                    {v.tittel ?? `Varsling #${v.id}`}
                  </span>
                  <span className="text-xs text-gray-500 shrink-0">
                    {v.tilbudsfrist?.slice(0, 10)} ({days}d)
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Kilde distribution */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <h2 className="text-sm font-semibold mb-4" style={{ color: '#1F3A5F' }}>
          Kunngjøringer per kilde
        </h2>
        {Object.keys(kildeTeller).length === 0 ? (
          <p className="text-sm text-gray-500">Ingen kunngjøringer i databasen ennå.</p>
        ) : (
          <div className="space-y-2">
            {Object.entries(kildeTeller).map(([kilde, count]) => (
              <SimpleBar
                key={kilde}
                label={kilde}
                value={count}
                max={maxKilde}
                color="#B08D2E"
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
