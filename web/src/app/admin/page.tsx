'use client'

import { useState, useEffect } from 'react'
import SectionHeader from '@/components/SectionHeader'
import MetricCard from '@/components/MetricCard'
import { triggerSync, fetchHealth, fetchKunngjøringer } from '@/lib/api'
import type { SyncResponse, HealthResponse } from '@/lib/types'

export default function AdminPage() {
  const [syncing, setSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState<SyncResponse | null>(null)
  const [syncError, setSyncError] = useState<string | null>(null)

  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [kunngjøringerCount, setKunngjøringerCount] = useState<number | null>(null)
  const [statusLoading, setStatusLoading] = useState(true)

  useEffect(() => {
    async function loadStatus() {
      try {
        const [h, k] = await Promise.all([
          fetchHealth(),
          fetchKunngjøringer(),
        ])
        setHealth(h)
        setKunngjøringerCount(k.length)
      } catch {
        // error handled below
      } finally {
        setStatusLoading(false)
      }
    }
    loadStatus()
  }, [])

  async function handleSync() {
    setSyncing(true)
    setSyncResult(null)
    setSyncError(null)
    try {
      const result = await triggerSync()
      setSyncResult(result)
      // Refresh count
      const k = await fetchKunngjøringer()
      setKunngjøringerCount(k.length)
    } catch (e) {
      setSyncError(e instanceof Error ? e.message : 'Synkroniseringsfeil')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div>
      <SectionHeader eyebrow="ADMINISTRASJON" title="⚙️ Admin og synkronisering" />
      <p className="text-sm text-gray-600 mb-6">
        Her kan du manuelt synkronisere kunngjøringer fra Doffin og TED, og se status på databasen.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Sync panel */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold mb-1" style={{ color: '#1F3A5F' }}>
            Manuell synkronisering
          </h2>
          <p className="text-xs text-gray-500 mb-4">
            Henter kunngjøringer fra de siste 2 dagene fra Doffin og TED.
          </p>
          <button
            onClick={handleSync}
            disabled={syncing}
            className="w-full px-4 py-2.5 rounded-lg text-sm font-semibold text-white disabled:opacity-50 transition-opacity"
            style={{ background: '#1F3A5F' }}
          >
            {syncing ? 'Synkroniserer...' : '🔄 Synkroniser nå'}
          </button>

          {syncResult && (
            <div className="mt-4 space-y-2">
              <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-2 text-sm font-medium">
                Synkronisering fullført!
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-xl font-bold" style={{ color: '#1F3A5F' }}>
                    {syncResult.nye_kunngjøringer}
                  </p>
                  <p className="text-xs text-gray-500">Nye kunngjøringer</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-xl font-bold" style={{ color: '#1F3A5F' }}>
                    {syncResult.nye_varsler}
                  </p>
                  <p className="text-xs text-gray-500">Nye varsler</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-xl font-bold" style={{ color: '#1F3A5F' }}>
                    {syncResult.totalt_hentet}
                  </p>
                  <p className="text-xs text-gray-500">Totalt hentet</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-sm font-medium" style={{ color: '#1F3A5F' }}>
                    Doffin: {syncResult.doffin} / TED: {syncResult.ted}
                  </p>
                  <p className="text-xs text-gray-500">Per kilde</p>
                </div>
              </div>
            </div>
          )}

          {syncError && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
              {syncError}
            </div>
          )}
        </div>

        {/* Status panel */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold mb-4" style={{ color: '#1F3A5F' }}>
            Databasestatus
          </h2>
          {statusLoading ? (
            <p className="text-sm text-gray-500 animate-pulse">Sjekker status...</p>
          ) : !health ? (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
              <p className="font-medium">API ikke tilgjengelig</p>
              <p className="mt-1 text-xs">
                Sørg for at backend kjører:{' '}
                <code className="bg-red-100 px-1 rounded">
                  uvicorn leverandor.api.main:app --reload
                </code>
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-green-700">
                <span>🟢</span>
                <span>API status: {health.status.toUpperCase()}</span>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-2xl font-bold" style={{ color: '#1F3A5F' }}>
                  {kunngjøringerCount ?? '—'}
                </p>
                <p className="text-xs text-gray-500">Kunngjøringer i DB</p>
              </div>
              <p className="text-xs text-gray-500">
                API versjon: <code className="bg-gray-100 px-1 rounded">{health.version}</code>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Config info */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
          Konfigurering
        </h2>
        <div className="text-sm text-gray-600 space-y-2">
          <p className="font-medium text-gray-700">Miljøvariabler (.env):</p>
          <ul className="space-y-1 text-xs">
            <li>
              <code className="bg-gray-100 px-1 rounded">DOFFIN_API_KEY</code> — API-nøkkel for
              Doffin Public API (valgfri — faller tilbake til CSV)
            </li>
            <li>
              <code className="bg-gray-100 px-1 rounded">DATABASE_URL</code> — Database URL
              (standard: sqlite:///./anbudsvarsler.db)
            </li>
            <li>
              <code className="bg-gray-100 px-1 rounded">ANTHROPIC_API_KEY</code> — For Phase 2
              PDF-parsing
            </li>
            <li>
              <code className="bg-gray-100 px-1 rounded">NEXT_PUBLIC_API_URL</code> — Pek på
              backend-URL (standard: http://localhost:8000)
            </li>
          </ul>
          <p className="mt-3 text-xs">
            Registrer Doffin API-nøkkel på{' '}
            <a
              href="https://dof-notices-prod-api.developer.azure-api.net/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
              style={{ color: '#1F3A5F' }}
            >
              dof-notices-prod-api.developer.azure-api.net
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
