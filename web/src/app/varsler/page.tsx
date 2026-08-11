'use client'

import { useState, useEffect, useCallback } from 'react'
import SectionHeader from '@/components/SectionHeader'
import StatusPill from '@/components/StatusPill'
import ResultatBadge from '@/components/ResultatBadge'
import {
  fetchVarsler,
  fetchKunngjøringer,
  fetchKvalifikasjoner,
  updateVarslingStatus,
  runKvalifikasjon,
} from '@/lib/api'
import type {
  Varsling,
  Kunngjoring,
  Kvalifikasjonssjekk,
  VarslingStatus,
} from '@/lib/types'
import { useProfile } from '@/hooks/useProfile'

const ALL_STATUSER: VarslingStatus[] = [
  'NY', 'SETT', 'INTERESSERT', 'FORKASTET', 'LEVERT', 'VUNNET', 'TAPT',
]

function formatNok(v: number | undefined | null): string {
  if (v == null) return 'Ikke oppgitt'
  return new Intl.NumberFormat('nb-NO', { maximumFractionDigits: 0 }).format(v) + ' NOK'
}

export default function VarslerPage() {
  const { profilId, loaded } = useProfile()
  const [varsler, setVarsler] = useState<Varsling[]>([])
  const [kunngjøringer, setKunngjøringer] = useState<Record<number, Kunngjoring>>({})
  const [sjekker, setSjekker] = useState<Record<number, Kvalifikasjonssjekk>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('Alle')
  const [minScore, setMinScore] = useState(0)
  const [sortBy, setSortBy] = useState<'relevans' | 'frist'>('relevans')

  // Per-card state
  const [pendingStatus, setPendingStatus] = useState<Record<number, VarslingStatus>>({})
  const [savingId, setSavingId] = useState<number | null>(null)
  const [kvalLoading, setKvalLoading] = useState<number | null>(null)

  const loadData = useCallback(async () => {
    if (!profilId) return
    setLoading(true)
    setError(null)
    try {
      const [v, k, s] = await Promise.all([
        fetchVarsler(profilId),
        fetchKunngjøringer(),
        fetchKvalifikasjoner({ profilId }),
      ])
      setVarsler(v)
      const kMap: Record<number, Kunngjoring> = {}
      k.forEach((kj) => { kMap[kj.id] = kj })
      setKunngjøringer(kMap)

      const sMap: Record<number, Kvalifikasjonssjekk> = {}
      // API returns newest first; we take the first (newest) per varsling
      s.forEach((sjekk) => {
        if (!(sjekk.varsling_id in sMap)) {
          sMap[sjekk.varsling_id] = sjekk
        }
      })
      setSjekker(sMap)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ukjent feil')
    } finally {
      setLoading(false)
    }
  }, [profilId])

  useEffect(() => {
    if (loaded && profilId) loadData()
  }, [loaded, profilId, loadData])

  // Filter + sort
  let displayed = [...varsler]
  if (statusFilter !== 'Alle') {
    displayed = displayed.filter((v) => v.status === statusFilter)
  }
  displayed = displayed.filter((v) => v.relevans_score >= minScore / 100)

  if (sortBy === 'frist') {
    displayed = displayed.sort((a, b) => {
      const fa = kunngjøringer[a.kunngjoring_id]?.tilbudsfrist ?? '9999'
      const fb = kunngjøringer[b.kunngjoring_id]?.tilbudsfrist ?? '9999'
      return fa.localeCompare(fb)
    })
  } else {
    displayed = displayed.sort((a, b) => b.relevans_score - a.relevans_score)
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
    } catch (e) {
      alert(`Feil ved lagring: ${e instanceof Error ? e.message : e}`)
    } finally {
      setSavingId(null)
    }
  }

  async function handleKvalifikasjon(varslingId: number) {
    if (!profilId) return
    setKvalLoading(varslingId)
    try {
      const result = await runKvalifikasjon(varslingId, profilId)
      setSjekker((prev) => ({ ...prev, [varslingId]: result }))
    } catch (e) {
      alert(`Kvalifikasjonsfeil: ${e instanceof Error ? e.message : e}`)
    } finally {
      setKvalLoading(null)
    }
  }

  if (!loaded) return null

  if (!profilId) {
    return (
      <div>
        <SectionHeader eyebrow="MINE VARSLER" title="🔔 Mine anbudsvarsler" />
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg p-4 text-sm">
          Du må velge en leverandørprofil. Profil-ID lagres i localStorage under &quot;profil_id&quot;.
          Sett den via utviklerverktøy eller kontakt administrator.
        </div>
      </div>
    )
  }

  return (
    <div>
      <SectionHeader eyebrow="MINE VARSLER" title="🔔 Mine anbudsvarsler" />

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Status</label>
          <select
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="Alle">Alle</option>
            {ALL_STATUSER.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Min relevans-score: {minScore}%
          </label>
          <input
            type="range"
            min={0}
            max={100}
            step={10}
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="w-40"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Sorter etter</label>
          <select
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'relevans' | 'frist')}
          >
            <option value="relevans">Relevans (høy til lav)</option>
            <option value="frist">Tilbudsfrist (nærmest først)</option>
          </select>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50"
          style={{ background: '#1F3A5F' }}
        >
          {loading ? 'Laster...' : 'Oppdater'}
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-sm text-gray-500 animate-pulse">Laster varsler...</div>
      ) : displayed.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-lg p-4 text-sm">
          Ingen varsler funnet. Juster filtrene eller kjør en synkronisering fra Admin-siden.
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Viser <strong>{displayed.length}</strong> varsler
          </p>
          <div className="space-y-4">
            {displayed.map((v) => {
              const k = kunngjøringer[v.kunngjoring_id]
              const sjekk = sjekker[v.id]
              const currentStatus = pendingStatus[v.id] ?? v.status

              return (
                <div
                  key={v.id}
                  className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
                >
                  <div className="px-5 py-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 mb-1 truncate">
                          📄 {k?.tittel ?? 'Ukjent tittel'}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2">
                          {k?.oppdragsgiver ?? 'Ukjent oppdragsgiver'}
                        </p>
                        <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                          {k?.tilbudsfrist && (
                            <span>
                              Frist:{' '}
                              <strong>{k.tilbudsfrist.slice(0, 10)}</strong>
                            </span>
                          )}
                          <span>
                            Verdi:{' '}
                            <strong>{formatNok(k?.estimert_verdi)}</strong>
                          </span>
                          {k?.cpv_koder?.length && (
                            <span>
                              CPV: <strong>{k.cpv_koder.slice(0, 3).join(', ')}</strong>
                            </span>
                          )}
                        </div>
                        {k?.url && (
                          <a
                            href={k.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs underline mt-2 inline-block"
                            style={{ color: '#1F3A5F' }}
                          >
                            Åpne på {k.kilde ?? 'Doffin'}
                          </a>
                        )}
                      </div>

                      {/* Right column */}
                      <div className="flex flex-col items-end gap-2 shrink-0">
                        <StatusPill status={v.status} />
                        {sjekk && <ResultatBadge resultat={sjekk.resultat} />}
                        <span className="text-sm font-medium" style={{ color: '#1F3A5F' }}>
                          {(v.relevans_score * 100).toFixed(0)}% relevans
                        </span>

                        {/* Status update */}
                        <div className="flex gap-2 items-center">
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
                          <button
                            onClick={() => handleSaveStatus(v.id)}
                            disabled={savingId === v.id || currentStatus === v.status}
                            className="px-2 py-1 rounded text-xs font-medium text-white disabled:opacity-40"
                            style={{ background: '#1F3A5F' }}
                          >
                            {savingId === v.id ? '...' : 'Lagre'}
                          </button>
                        </div>

                        <button
                          onClick={() => handleKvalifikasjon(v.id)}
                          disabled={kvalLoading === v.id}
                          className="px-3 py-1 rounded text-xs font-medium text-white disabled:opacity-40"
                          style={{ background: '#B08D2E' }}
                        >
                          {kvalLoading === v.id ? 'Sjekker...' : 'Sjekk kvalifikasjon'}
                        </button>
                      </div>
                    </div>

                    {/* Qualification result detail */}
                    {sjekk && (sjekk.mangler.length > 0 || sjekk.diskvalifiserende.length > 0) && (
                      <div className="mt-3 pt-3 border-t border-gray-100 text-xs space-y-1">
                        {sjekk.diskvalifiserende.map((d, i) => (
                          <div key={i} className="text-red-600">
                            🚫 {d}
                          </div>
                        ))}
                        {sjekk.mangler.map((m, i) => (
                          <div key={i} className="text-yellow-600">
                            ⚠️ {m}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
