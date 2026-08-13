'use client'

import { useState, useEffect } from 'react'
import SectionHeader from '@/components/SectionHeader'
import { fetchDokumenter } from '@/lib/api'
import type { FirmaDokument } from '@/lib/types'
import { useProfile } from '@/hooks/useProfile'

type Tab = 'dokumenter' | 'maler' | 'referanser'

const DOKUMENT_KATEGORIER: Record<string, string> = {
  hms_erklæring: 'HMS-erklæring (§5 HMS-forskriften)',
  skatteattest: 'Skatteattester (Skatteetaten + kommunen)',
  firmaattest: 'Firmaattest fra Brønnøysund',
  forsikringsbevis: 'Forsikringsbevis',
  årsregnskap: 'Årsregnskap (siste 2 år)',
  iso_sertifikat: 'ISO-sertifikat',
  hms_kort: 'HMS-kort',
  egenerklæring: 'Etisk egenerklæring',
  egenerklæring_russland: 'Egenerklæring russiske selskaper (FOA §24-2)',
  annet: 'Annet dokument',
}

const UTLOEP_MÅNEDER: Record<string, number | null> = {
  skatteattest: 6,
  firmaattest: 3,
  forsikringsbevis: 12,
  årsregnskap: 24,
  iso_sertifikat: 36,
  hms_kort: 24,
  hms_erklæring: null,
  egenerklæring: null,
  egenerklæring_russland: null,
  annet: null,
}

function expiryIcon(dok: FirmaDokument): string {
  if (!dok.lastet_opp) return '⬜'
  if (!dok.utloep_dato) return '✅'
  const dager = Math.floor(
    (new Date(dok.utloep_dato).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  )
  if (dager < 0) return '🔴'
  if (dager <= 30) return '🟡'
  return '✅'
}

const MALER = [
  { navn: 'HMS-erklæring mal', beskrivelse: 'Standard HMS-erklæring etter HMS-forskriften §5', url: '#' },
  { navn: 'Etisk egenerklæring mal', beskrivelse: 'DFØs mal for etisk egenerklæring', url: '#' },
  { navn: 'Referanseprosjekt-mal', beskrivelse: 'Mal for å dokumentere referanseprosjekter (FOA §16-8)', url: '#' },
  { navn: 'ESPD-skjema', beskrivelse: 'Europeisk egenerklæring (DFØs offisielle mal)', url: 'https://www.dfo.no/fagomrader/anskaffelser/espd' },
  { navn: 'Tilbudsbrev mal', beskrivelse: 'Standard tilbudsbekreftelse til oppdragsgiver', url: '#' },
]

const REFERANSER = [
  { tittel: 'Doffin — norsk kunngjøringsportal', url: 'https://doffin.no' },
  { tittel: 'TED — europeisk kunngjøringsportal', url: 'https://ted.europa.eu' },
  { tittel: 'DFØ — ESPD-veileder', url: 'https://www.dfo.no/fagomrader/anskaffelser/espd' },
  { tittel: 'Brønnøysundregistrene — firmaattest', url: 'https://brreg.no' },
  { tittel: 'Skatteetaten — skatteattest', url: 'https://www.skatteetaten.no/bedrift-og-organisasjon/starte-og-drive/skatteattest/' },
  { tittel: 'Lovdata — FOA (Anskaffelsesforskriften)', url: 'https://lovdata.no/dokument/SF/forskrift/2016-08-12-974' },
  { tittel: 'DFØ — SSA-avtalemaler', url: 'https://www.dfo.no/fagomrader/anskaffelser/statens-standardavtaler' },
  { tittel: 'Startbank — leverandørregistrering', url: 'https://www.startbank.no' },
]

export default function BibliotekPage() {
  const { profilId, loaded } = useProfile()
  const [activeTab, setActiveTab] = useState<Tab>('dokumenter')
  const [dokumenter, setDokumenter] = useState<FirmaDokument[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (loaded && profilId) {
      setLoading(true)
      fetchDokumenter(profilId)
        .then(setDokumenter)
        .catch(() => setDokumenter([]))
        .finally(() => setLoading(false))
    }
  }, [loaded, profilId])

  // Group documents by category
  const docByKategori: Record<string, FirmaDokument[]> = {}
  dokumenter.forEach((d) => {
    if (!docByKategori[d.kategori]) docByKategori[d.kategori] = []
    docByKategori[d.kategori].push(d)
  })

  return (
    <div>
      <SectionHeader eyebrow="INNHOLDSBIBLIOTEK" title="📚 Innholdsbibliotek" />

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 w-fit">
        {(
          [
            { key: 'dokumenter', label: 'Dokumenter' },
            { key: 'maler', label: 'Maler' },
            { key: 'referanser', label: 'Referanser' },
          ] as { key: Tab; label: string }[]
        ).map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={
              activeTab === key
                ? { background: '#1F3A5F', color: '#fff' }
                : { color: '#6b7280' }
            }
          >
            {label}
          </button>
        ))}
      </div>

      {/* Dokumenter */}
      {activeTab === 'dokumenter' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          {!profilId ? (
            <p className="text-sm text-gray-500">
              Gå til <a href="/profil" className="underline font-medium">Min Profil</a> for å opprette en profil.
            </p>
          ) : loading ? (
            <p className="text-sm text-gray-500 animate-pulse">Laster dokumenter...</p>
          ) : dokumenter.length === 0 ? (
            <div>
              <p className="text-sm text-gray-500 mb-4">
                Ingen dokumenter registrert ennå. Her er en oversikt over hva du bør ha:
              </p>
              <div className="space-y-3">
                {Object.entries(DOKUMENT_KATEGORIER).map(([kat, navn]) => {
                  const mnd = UTLOEP_MÅNEDER[kat]
                  return (
                    <div
                      key={kat}
                      className="flex items-center gap-3 p-3 rounded-lg border border-gray-100 bg-gray-50"
                    >
                      <span className="text-lg">⬜</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{navn}</p>
                        {mnd && (
                          <p className="text-xs text-gray-400">Utløper etter {mnd} måneder</p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-700">
                ✅ = gyldig &nbsp;|&nbsp; 🟡 = utløper snart (&lt;30d) &nbsp;|&nbsp; 🔴 = utløpt &nbsp;|&nbsp; ⬜ = ikke lastet opp
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(docByKategori).map(([kat, docs]) => (
                <div key={kat}>
                  <h3 className="text-xs font-semibold uppercase text-gray-500 mb-2">
                    {DOKUMENT_KATEGORIER[kat] ?? kat}
                  </h3>
                  <div className="space-y-2">
                    {docs.map((d) => (
                      <div
                        key={d.id}
                        className="flex items-center gap-3 p-3 rounded-lg border border-gray-200"
                      >
                        <span className="text-lg">{expiryIcon(d)}</span>
                        <div className="flex-1">
                          <p className="text-sm font-medium">{d.navn}</p>
                          {d.utloep_dato && (
                            <p className="text-xs text-gray-400">
                              Utløper: {d.utloep_dato.slice(0, 10)}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Maler */}
      {activeTab === 'maler' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <p className="text-sm text-gray-600 mb-4">
            Standardmaler du kan bruke i tilbudsprosessen.
          </p>
          <div className="space-y-3">
            {MALER.map((m) => (
              <div
                key={m.navn}
                className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50"
              >
                <span className="text-lg shrink-0">📄</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">{m.navn}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{m.beskrivelse}</p>
                </div>
                <a
                  href={m.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-medium underline shrink-0"
                  style={{ color: '#1F3A5F' }}
                >
                  Åpne
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Referanser */}
      {activeTab === 'referanser' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <p className="text-sm text-gray-600 mb-4">
            Nyttige lenker og ressurser for offentlig anskaffelse.
          </p>
          <div className="space-y-2">
            {REFERANSER.map((r) => (
              <div key={r.tittel} className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50">
                <span className="text-lg shrink-0">🔗</span>
                <a
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium underline flex-1"
                  style={{ color: '#1F3A5F' }}
                >
                  {r.tittel}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
