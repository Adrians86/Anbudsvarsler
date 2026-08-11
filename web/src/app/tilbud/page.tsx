'use client'

import { useState } from 'react'
import SectionHeader from '@/components/SectionHeader'
import { SSA_MAP, SSA_TYPES, detectSsa } from '@/lib/ssaData'

type Tab = 'sjekkliste' | 'espd' | 'ssa'

const SJEKKLISTE_ITEMS = [
  { id: 'frist', tekst: 'Noter tilbudsfristen og sett alarm 5 dager i forveien' },
  { id: 'les_krav', tekst: 'Les kravspesifikasjonen nøye fra start til slutt' },
  { id: 'cpv', tekst: 'Bekreft at dine CPV-koder matcher kunngjøringen' },
  { id: 'verdi', tekst: 'Sjekk om estimert verdi er innenfor din kapasitet' },
  { id: 'skatteatt', tekst: 'Hent ferske skatteattester (< 6 mnd) fra skatteetaten.no' },
  { id: 'firmaatt', tekst: 'Hent fersk firmaattest (< 3 mnd) fra brreg.no' },
  { id: 'hms', tekst: 'Forbered HMS-erklæring signert av øverste leder' },
  { id: 'forsikring', tekst: 'Vedlegg gyldig forsikringsbevis' },
  { id: 'referanser', tekst: 'Legg ved minst ett referanseprosjekt med kontaktinfo' },
  { id: 'espd', tekst: 'Fyll ut ESPD-skjema (DFØs mal) for alle deler I–VI' },
  { id: 'ssa_bilag', tekst: 'Fyll ut alle påkrevde SSA-bilag for kontraktstypen' },
  { id: 'pris', tekst: 'Utarbeid tilbudspris med detaljert prisliste (Bilag 2)' },
  { id: 'underlev', tekst: 'List opp underleverandører i Bilag 7 (SSA-T) om relevant' },
  { id: 'gjennomles', tekst: 'Gjennomles hele tilbudet med en kollega før innsending' },
  { id: 'lever', tekst: 'Send inn via Doffin/TED-portal i god tid før fristen' },
]

const ESPD_DELER = [
  {
    del: 'Del I',
    tittel: 'Informasjon om anskaffelsesprosedyren',
    innhold: [
      'Kontraktsoppdragets tittel og referansenummer',
      'Oppdragsgivers navn og kontaktinformasjon',
      'CPV-kode(r) og NUTS-region for leveransen',
    ],
  },
  {
    del: 'Del II',
    tittel: 'Informasjon om leverandøren',
    innhold: [
      'Foretaksnavn og organisasjonsnummer',
      'Kontaktperson, adresse, e-post og telefon',
      'Opplysninger om ev. underleverandører',
    ],
  },
  {
    del: 'Del III',
    tittel: 'Utelukkelsesgrunnlag (FOA §24-2)',
    innhold: [
      '§24-2 a) — Ikke rettskraftig domfelt',
      '§24-2 b) — Ikke i mislighold av skatte-/avgiftsforpliktelser',
      '§24-2 c) — Ikke under konkursbehandling',
      '§24-2 d) — Ikke skyldig i alvorlig yrkesfeil',
      '§24-2 e–g) — Ingen interessekonflikt / påvirkning',
      'Egenerklæring Russland-tilknyttede selskaper',
    ],
  },
  {
    del: 'Del IV',
    tittel: 'Kvalifikasjonskrav (FOA kap. 16)',
    innhold: [
      '§16-2 — Skatteattester (< 6 mnd)',
      '§16-3 — HMS-erklæring',
      '§16-4 — Finansiell kapasitet (omsetning ≥ 2× kontraktsverdi)',
      '§16-5 — Forsikringsbevis',
      '§16-6 — Faglig kompetanse (CPV-overlapp)',
      '§16-8 — Referanseprosjekter (min. 1 siste 3 år)',
    ],
  },
  {
    del: 'Del V',
    tittel: 'Reduksjon av antall kandidater',
    innhold: [
      'Kun relevant ved begrenset anbudskonkurranse',
      'Angi tilleggskriterier for utvelgelse om påkrevd',
    ],
  },
  {
    del: 'Del VI',
    tittel: 'Avsluttende erklæringer',
    innhold: [
      'Bekreft at opplysningene er korrekte',
      'Dato og signatur fra autorisert representant',
    ],
  },
]

export default function TilbudPage() {
  const [activeTab, setActiveTab] = useState<Tab>('sjekkliste')
  const [checked, setChecked] = useState<Record<string, boolean>>({})
  const [selectedSsa, setSelectedSsa] = useState('SSA-T')
  const [openEspd, setOpenEspd] = useState<number | null>(null)

  function toggleCheck(id: string) {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const checkedCount = Object.values(checked).filter(Boolean).length
  const total = SJEKKLISTE_ITEMS.length
  const progressPct = Math.round((checkedCount / total) * 100)

  const ssaInfo = SSA_MAP[selectedSsa]

  return (
    <div>
      <SectionHeader eyebrow="TILBUDSSTØTTE" title="📋 Tilbudsstøtte" />

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 w-fit">
        {(
          [
            { key: 'sjekkliste', label: 'Sjekkliste' },
            { key: 'espd', label: 'ESPD-guide' },
            { key: 'ssa', label: 'SSA-bilag' },
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

      {/* Sjekkliste tab */}
      {activeTab === 'sjekkliste' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">
              {checkedCount} av {total} punkter fullført
            </p>
            <span className="text-sm font-semibold" style={{ color: '#1F3A5F' }}>
              {progressPct}%
            </span>
          </div>
          {/* Progress bar */}
          <div className="h-2 bg-gray-100 rounded-full mb-5 overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${progressPct}%`,
                background: progressPct === 100 ? '#2ECC71' : '#1F3A5F',
              }}
            />
          </div>

          <div className="space-y-3">
            {SJEKKLISTE_ITEMS.map((item) => (
              <label
                key={item.id}
                className="flex items-start gap-3 cursor-pointer group"
              >
                <input
                  type="checkbox"
                  checked={!!checked[item.id]}
                  onChange={() => toggleCheck(item.id)}
                  className="mt-0.5 w-4 h-4 rounded accent-navy shrink-0"
                />
                <span
                  className={`text-sm ${checked[item.id] ? 'line-through text-gray-400' : 'text-gray-700'}`}
                >
                  {item.tekst}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* ESPD guide tab */}
      {activeTab === 'espd' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <p className="text-sm text-gray-600 mb-4">
            Europeisk egenerklæring (ESPD) er obligatorisk for alle EU/EØS-anskaffelser over
            terskelverdier. Bruk DFØs offisielle skjema fra{' '}
            <a
              href="https://www.dfo.no/fagomrader/anskaffelser/espd"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
              style={{ color: '#1F3A5F' }}
            >
              dfo.no
            </a>
            .
          </p>
          <div className="space-y-2">
            {ESPD_DELER.map((del, i) => (
              <div key={i} className="border border-gray-200 rounded-lg overflow-hidden">
                <button
                  className="w-full text-left px-4 py-3 flex items-center justify-between text-sm font-medium bg-gray-50 hover:bg-gray-100"
                  onClick={() => setOpenEspd(openEspd === i ? null : i)}
                >
                  <span>
                    <span className="font-bold mr-2">{del.del}</span> {del.tittel}
                  </span>
                  <span className="text-gray-400">{openEspd === i ? '▲' : '▼'}</span>
                </button>
                {openEspd === i && (
                  <div className="px-4 py-3">
                    <ul className="space-y-1">
                      {del.innhold.map((punkt, j) => (
                        <li key={j} className="text-sm text-gray-600 flex gap-2">
                          <span className="text-gray-400 shrink-0">•</span>
                          {punkt}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SSA bilag tab */}
      {activeTab === 'ssa' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex gap-2 flex-wrap mb-5">
            {SSA_TYPES.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedSsa(type)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors"
                style={
                  selectedSsa === type
                    ? { background: '#1F3A5F', color: '#fff', borderColor: '#1F3A5F' }
                    : { background: '#fff', color: '#555', borderColor: '#d1d5db' }
                }
              >
                {type}
              </button>
            ))}
          </div>

          {ssaInfo && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="font-semibold">{ssaInfo.navn}</span>
                <span
                  className="px-2 py-0.5 rounded text-xs font-bold"
                  style={{
                    background:
                      ssaInfo.risiko_nivå === 'HØY'
                        ? '#fee2e2'
                        : ssaInfo.risiko_nivå.startsWith('MIDDELS')
                          ? '#fef3c7'
                          : '#d1fae5',
                    color:
                      ssaInfo.risiko_nivå === 'HØY'
                        ? '#991b1b'
                        : ssaInfo.risiko_nivå.startsWith('MIDDELS')
                          ? '#92400e'
                          : '#065f46',
                  }}
                >
                  Risiko: {ssaInfo.risiko_nivå}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-4">{ssaInfo.beskrivelse}</p>

              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
                  Risikoer
                </p>
                <ul className="space-y-1.5 text-sm text-gray-700">
                  {ssaInfo.risiko.map((r, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="shrink-0">⚠️</span> {r}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
                  Obligatoriske bilag
                </p>
                <ul className="space-y-1.5 text-sm text-gray-700">
                  {ssaInfo.bilag.map((b, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-green-600 shrink-0">✓</span> {b}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
