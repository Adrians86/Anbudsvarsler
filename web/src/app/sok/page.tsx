'use client'

import { useState } from 'react'
import SectionHeader from '@/components/SectionHeader'
import StatusPill from '@/components/StatusPill'
import { fetchKunngjøringer, fetchVarsler } from '@/lib/api'
import type { Kunngjoring, Varsling } from '@/lib/types'
import { CPV_GRUPPER, NUTS_REGIONER, cpvKode } from '@/lib/cpvData'
import { useProfile } from '@/hooks/useProfile'

function formatNok(v: number | undefined | null): string {
  if (v == null) return 'Ikke oppgitt'
  return new Intl.NumberFormat('nb-NO', { maximumFractionDigits: 0 }).format(v) + ' NOK'
}

export default function SokPage() {
  const { profilId } = useProfile()
  const [selectedCpv, setSelectedCpv] = useState<Record<string, boolean>>({})
  const [region, setRegion] = useState('')
  const [minNok, setMinNok] = useState(0)
  const [maxNok, setMaxNok] = useState(0)

  const [results, setResults] = useState<Kunngjoring[] | null>(null)
  const [varslingMap, setVarslingMap] = useState<Record<number, Varsling>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function resetFilters() {
    setSelectedCpv({})
    setRegion('')
    setMinNok(0)
    setMaxNok(0)
    setResults(null)
  }

  function toggleCpv(kode: string) {
    setSelectedCpv((prev) => ({ ...prev, [kode]: !prev[kode] }))
  }

  async function handleSok() {
    setLoading(true)
    setError(null)

    // Collect selected CPV codes
    const valgteCpvStrings = Object.keys(selectedCpv).filter((k) => selectedCpv[k])
    const valgteCpvKoder = new Set(valgteCpvStrings.map(cpvKode))

    // Use first CPV code for API filter (API supports one at a time)
    const firstCpv = [...valgteCpvKoder][0]

    try {
      const params: { cpv?: string; region?: string } = {}
      if (firstCpv) params.cpv = firstCpv
      if (region) params.region = region

      let kunngjøringer = await fetchKunngjøringer(params)

      // Client-side multi-CPV filter
      if (valgteCpvKoder.size > 1) {
        kunngjøringer = kunngjøringer.filter((k) =>
          k.cpv_koder?.some((c) => valgteCpvKoder.has(c))
        )
      }

      // Value filters
      if (minNok > 0) {
        kunngjøringer = kunngjøringer.filter((k) => {
          const v = k.estimert_verdi
          return v != null && Number(v) >= minNok
        })
      }
      if (maxNok > 0) {
        kunngjøringer = kunngjøringer.filter((k) => {
          const v = k.estimert_verdi
          return v == null || Number(v) <= maxNok
        })
      }

      setResults(kunngjøringer)

      // Load varsling map for current profile
      if (profilId) {
        try {
          const varsler = await fetchVarsler(profilId)
          const vm: Record<number, Varsling> = {}
          varsler.forEach((v) => { vm[v.kunngjoring_id] = v })
          setVarslingMap(vm)
        } catch {
          // not critical
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ukjent søkefeil')
    } finally {
      setLoading(false)
    }
  }

  const bransjer = Object.entries(CPV_GRUPPER)

  return (
    <div>
      <SectionHeader eyebrow="SØK I KUNNGJØRINGER" title="🔍 Søk etter kunngjøringer" />

      {/* CPV filter */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
          Filtrer på bransje / CPV-kode
        </h2>
        <div className="grid grid-cols-2 gap-x-6 gap-y-4">
          {bransjer.map(([bransje, koder]) => (
            <div key={bransje}>
              <p className="text-xs font-semibold text-gray-500 mb-1">{bransje}</p>
              <div className="space-y-1">
                {koder.map((kode) => (
                  <label key={kode} className="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="checkbox"
                      checked={!!selectedCpv[kode]}
                      onChange={() => toggleCpv(kode)}
                      className="rounded"
                    />
                    {kode}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Other filters */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4 grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">NUTS-region</label>
          <select
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          >
            {Object.entries(NUTS_REGIONER).map(([label, val]) => (
              <option key={label} value={val}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Min verdi (NOK)</label>
            <input
              type="number"
              min={0}
              step={100000}
              value={minNok || ''}
              onChange={(e) => setMinNok(Number(e.target.value))}
              placeholder="0"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Maks verdi (NOK)</label>
            <input
              type="number"
              min={0}
              step={500000}
              value={maxNok || ''}
              onChange={(e) => setMaxNok(Number(e.target.value))}
              placeholder="Ingen grense"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={handleSok}
          disabled={loading}
          className="px-6 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
          style={{ background: '#1F3A5F' }}
        >
          {loading ? 'Søker...' : 'Søk'}
        </button>
        <button
          onClick={resetFilters}
          className="px-6 py-2 rounded-lg text-sm font-semibold border border-gray-300 text-gray-700 bg-white hover:bg-gray-50"
        >
          Nullstill filtre
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {results === null ? (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-lg p-4 text-sm">
          <p className="font-semibold mb-2">Tips:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Velg én eller flere bransjer fra listen over</li>
            <li>Bruk NUTS-region for å filtrere geografisk</li>
            <li>Bruk verdifiltrene for å begrense etter estimert kontraktsverdi</li>
            <li>Trykk Søk uten filtre for å se alle kunngjøringer i databasen</li>
          </ul>
        </div>
      ) : results.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 text-gray-600 rounded-lg p-4 text-sm">
          Ingen kunngjøringer funnet med valgte filtre.
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Fant <strong>{results.length}</strong> kunngjøringer
          </p>
          <div className="space-y-3">
            {results.map((k) => {
              const varsling = varslingMap[k.id]
              return (
                <div
                  key={k.id}
                  className="bg-white rounded-xl border border-gray-200 shadow-sm p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 mb-1">
                        📄 {k.tittel}
                      </h3>
                      <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-2">
                        <span>
                          <strong>Oppdragsgiver:</strong> {k.oppdragsgiver}
                        </span>
                        <span>
                          <strong>Kilde:</strong> {k.kilde}
                        </span>
                        {k.publisert && (
                          <span>
                            <strong>Publisert:</strong> {k.publisert.slice(0, 10)}
                          </span>
                        )}
                        {k.tilbudsfrist && (
                          <span>
                            <strong>Frist:</strong> {k.tilbudsfrist.slice(0, 10)}
                          </span>
                        )}
                        {k.nuts_region && (
                          <span>
                            <strong>Region:</strong> {k.nuts_region}
                          </span>
                        )}
                        {k.cpv_koder?.length && (
                          <span>
                            <strong>CPV:</strong> {k.cpv_koder.join(', ')}
                          </span>
                        )}
                      </div>
                      {k.url && (
                        <a
                          href={k.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs underline"
                          style={{ color: '#1F3A5F' }}
                        >
                          Åpne kunngjøring
                        </a>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-2 shrink-0">
                      <span className="text-sm font-semibold" style={{ color: '#1F3A5F' }}>
                        {formatNok(k.estimert_verdi)}
                      </span>
                      {varsling && (
                        <>
                          <StatusPill status={varsling.status} />
                          <span className="text-xs text-gray-400">Allerede i dine varsler</span>
                        </>
                      )}
                    </div>
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
