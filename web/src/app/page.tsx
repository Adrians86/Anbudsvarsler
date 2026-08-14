'use client'

import { useEffect, useState } from 'react'
import SectionHeader from '@/components/SectionHeader'
import MetricCard from '@/components/MetricCard'
import { fetchHealth, fetchKunngjøringer, triggerSync } from '@/lib/api'
import type { HealthResponse } from '@/lib/types'

export default function HjemPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthError, setHealthError] = useState(false)
  const [kunngjøringerCount, setKunngjøringerCount] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const h = await fetchHealth()
        setHealth(h)
      } catch {
        setHealthError(true)
      }
      try {
        const k = await fetchKunngjøringer()
        setKunngjøringerCount(k.length)
      } catch {
        setKunngjøringerCount(null)
      }
      setLoading(false)
    }
    load()
  }, [])

  async function handleSync() {
    setSyncing(true)
    setToast(null)
    try {
      const result = await triggerSync()
      const k = await fetchKunngjøringer()
      setKunngjøringerCount(k.length)
      setToast({ type: 'success', message: `Synkronisert: ${result.nye_kunngjøringer} nye kunngjøringer` })
    } catch (e) {
      setToast({ type: 'error', message: e instanceof Error ? e.message : 'Synkroniseringsfeil' })
    } finally {
      setSyncing(false)
      setTimeout(() => setToast(null), 5000)
    }
  }

  return (
    <div>
      <SectionHeader eyebrow="ANBUDSVARSLER" title="📋 Anbudsvarsler" />

      {/* Health banner */}
      <div className="mb-6">
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="animate-pulse">Sjekker API-status...</span>
          </div>
        ) : healthError ? (
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            <span>🔴</span>
            <span>API ikke tilgjengelig — sørg for at backend kjører på NEXT_PUBLIC_API_URL</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
            <span>🟢</span>
            <span>
              API tilgjengelig — versjon {health?.version ?? '?'}
            </span>
          </div>
        )}
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <MetricCard
          label="Totalt varsler"
          value={kunngjøringerCount !== null ? kunngjøringerCount : '—'}
          sub="Kunngjøringer i databasen"
          icon="📄"
        />
        <MetricCard
          label="Datakilder"
          value="Doffin + TED"
          sub="Europeisk og norsk innkjøpsportal"
          icon="🌐"
        />
        <MetricCard
          label="Oppdatering"
          value="Daglig kl. 06:00"
          sub="Automatisk synkronisering"
          icon="🔄"
        />
      </div>

      {/* Sync button + toast */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-60"
          style={{ background: '#1F3A5F', color: '#fff' }}
        >
          {syncing ? 'Oppdaterer...' : '🔄 Oppdater kunngjøringer'}
        </button>
        {toast && (
          <span
            className={`text-sm px-3 py-1 rounded-lg border ${
              toast.type === 'success'
                ? 'bg-green-50 border-green-200 text-green-700'
                : 'bg-red-50 border-red-200 text-red-700'
            }`}
          >
            {toast.message}
          </span>
        )}
      </div>

      {/* Quick links */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 className="text-base font-semibold mb-4" style={{ color: '#1F3A5F' }}>
          Kom i gang
        </h2>
        <ul className="space-y-2 text-sm text-gray-600">
          <li>
            <span className="text-base mr-2">🔔</span>
            Gå til{' '}
            <a href="/varsler" className="underline" style={{ color: '#1F3A5F' }}>
              Mine Varsler
            </a>{' '}
            for å se relevante kunngjøringer for din profil.
          </li>
          <li>
            <span className="text-base mr-2">🔍</span>
            Bruk{' '}
            <a href="/sok" className="underline" style={{ color: '#1F3A5F' }}>
              Søk
            </a>{' '}
            for å søke i alle kunngjøringer etter bransje, region og verdi.
          </li>
          <li>
            <span className="text-base mr-2">✅</span>
            Kjør{' '}
            <a href="/kvalifikasjon" className="underline" style={{ color: '#1F3A5F' }}>
              Kvalifikasjonssjekk
            </a>{' '}
            (GO / NO-GO) mot FOA kap. 16.
          </li>
          <li>
            <span className="text-base mr-2">⏰</span>
            Følg med på{' '}
            <a href="/frister" className="underline" style={{ color: '#1F3A5F' }}>
              Frister
            </a>{' '}
            for innkommende tilbudsfrister.
          </li>
          <li>
            <span className="text-base mr-2">⚙️</span>
            Gå til{' '}
            <a href="/admin" className="underline" style={{ color: '#1F3A5F' }}>
              Admin
            </a>{' '}
            for å synkronisere kunngjøringer manuelt.
          </li>
        </ul>
      </div>
    </div>
  )
}
