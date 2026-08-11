'use client'

import { useState, useEffect } from 'react'
import SectionHeader from '@/components/SectionHeader'
import ResultatBadge from '@/components/ResultatBadge'
import {
  fetchVarsler,
  fetchKunngjøring,
  runKvalifikasjon,
} from '@/lib/api'
import type { Varsling, Kunngjoring, Kvalifikasjonssjekk } from '@/lib/types'
import { useProfile } from '@/hooks/useProfile'
import { SSA_MAP, SSA_TYPES, detectSsa } from '@/lib/ssaData'

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
      'Foretaksnavn og organisasjonsnummer (NO: org.nr.)',
      'Kontaktperson, adresse, e-post og telefon',
      'Opplysninger om ev. underleverandører (Bilag 7 SSA-T)',
    ],
  },
  {
    del: 'Del III',
    tittel: 'Utelukkelsesgrunnlag (FOA §24-2)',
    innhold: [
      '§24-2 a) — Ikke rettskraftig domfelt for §§ nevnt i loven',
      '§24-2 b) — Ikke i alvorlig mislighold av skatte- og avgiftsforpliktelser',
      '§24-2 c) — Ikke under konkursbehandling e.l.',
      '§24-2 d) — Ikke funnet skyldig i alvorlig yrkesfeil',
      '§24-2 e) — Ikke lagt hindringer i veien for korreksjonsmekanismer',
      '§24-2 f) — Ingen interessekonflikt med oppdragsgiver',
      '§24-2 g) — Ingen urettmessig påvirkning av anskaffelsesprosessen',
      'Egenerklæring Russland-tilknyttede selskaper (EU-forordning 2022/576)',
    ],
  },
  {
    del: 'Del IV',
    tittel: 'Kvalifikasjonskrav (FOA kap. 16)',
    innhold: [
      '§16-2 — Gyldige skatteattester (< 6 mnd, Skatteetaten + kommune)',
      '§16-3 — HMS-erklæring signert av øverste leder',
      '§16-4 — Finansiell kapasitet (min. 2× estimert kontraktsverdi i omsetning)',
      '§16-5 — Forsikringsbevis gyldig forsikring',
      '§16-6 — Faglig kompetanse og teknisk kapasitet (CPV-overlapp)',
      '§16-8 — Minst ett referanseprosjekt siste 3 år',
    ],
  },
  {
    del: 'Del V',
    tittel: 'Reduksjon av antall kandidater',
    innhold: [
      'Kun relevant ved begrenset anbudskonkurranse / konkurranse med forhandling',
      'Angi ev. tilleggskriterier for utvelgelse av kandidater til innbydelse',
    ],
  },
  {
    del: 'Del VI',
    tittel: 'Avsluttende erklæringer',
    innhold: [
      'Bekreft at opplysningene er korrekte og at originaldokumentasjon kan fremlegges',
      'Dato og signatur fra autorisert representant',
    ],
  },
]

const VANLIGE_FEIL = [
  'Skatteattester eldre enn 6 måneder — hent nye fra skatteetaten.no',
  'Firmaattest eldre enn 3 måneder — hent fra brreg.no',
  'HMS-erklæringen er ikke signert av øverste leder',
  'Manglende egenerklæring for russisk tilknyttede selskaper (krav fra 2022)',
  'Omsetning dokumentert med feil regnskapsår — bruk siste to år',
  'CPV-koder i profilen samsvarer ikke med kunngjøringens CPV-koder',
  'ESPD-skjema fylt ut på feil mal (bruk DFØs gjeldende versjon)',
  'Forsikringsbevis er utløpt eller dekker ikke riktig risiko',
  'Ingen referanseprosjekter registrert i profilen',
  'Bilag 7 (underleverandørliste) mangler for SSA-T kontrakter',
]

export default function KvalifikasjonPage() {
  const { profilId, loaded } = useProfile()
  const [varsler, setVarsler] = useState<Varsling[]>([])
  const [selectedVarslingId, setSelectedVarslingId] = useState<number | null>(null)
  const [kunngjoring, setKunngjoring] = useState<Kunngjoring | null>(null)
  const [sjekk, setSjekk] = useState<Kvalifikasjonssjekk | null>(null)
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // SSA
  const [selectedSsa, setSelectedSsa] = useState('SSA-B')
  const [openEspd, setOpenEspd] = useState<number | null>(null)

  useEffect(() => {
    if (loaded && profilId) {
      fetchVarsler(profilId).then(setVarsler).catch(() => setVarsler([]))
    }
  }, [loaded, profilId])

  useEffect(() => {
    if (selectedVarslingId == null) {
      setKunngjoring(null)
      setSjekk(null)
      return
    }
    const v = varsler.find((x) => x.id === selectedVarslingId)
    if (!v) return
    setLoading(true)
    fetchKunngjøring(v.kunngjoring_id)
      .then((k) => {
        setKunngjoring(k)
        // Auto-detect SSA type
        setSelectedSsa(detectSsa(k.cpv_koder ?? [], k.tittel))
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [selectedVarslingId, varsler])

  async function handleKjørSjekk() {
    if (!profilId || !selectedVarslingId) return
    setRunning(true)
    setError(null)
    try {
      const result = await runKvalifikasjon(selectedVarslingId, profilId)
      setSjekk(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Feil ved sjekk')
    } finally {
      setRunning(false)
    }
  }

  if (!loaded) return null

  if (!profilId) {
    return (
      <div>
        <SectionHeader eyebrow="KVALIFIKASJONSSJEKK" title="✅ Kvalifikasjonssjekk" />
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg p-4 text-sm">
          Ingen profil valgt. Sett profil_id i localStorage.
        </div>
      </div>
    )
  }

  const ssaInfo = SSA_MAP[selectedSsa]

  return (
    <div>
      <SectionHeader eyebrow="KVALIFIKASJONSSJEKK" title="✅ Kvalifikasjonssjekk" />

      {/* Varsling selector */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Velg varsling å sjekke
        </label>
        <select
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
          value={selectedVarslingId ?? ''}
          onChange={(e) =>
            setSelectedVarslingId(e.target.value ? Number(e.target.value) : null)
          }
        >
          <option value="">-- Velg varsling --</option>
          {varsler.map((v) => (
            <option key={v.id} value={v.id}>
              [{v.status}] {v.tittel ?? `Varsling #${v.id}`} —{' '}
              {(v.relevans_score * 100).toFixed(0)}% relevans
            </option>
          ))}
        </select>
      </div>

      {/* Kunngjøring info */}
      {loading && (
        <div className="text-sm text-gray-500 animate-pulse mb-4">Laster kunngjøring...</div>
      )}

      {kunngjoring && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <h2 className="font-semibold mb-3" style={{ color: '#1F3A5F' }}>
            {kunngjoring.tittel}
          </h2>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm text-gray-600">
            <div>
              <span className="font-medium">Oppdragsgiver:</span> {kunngjoring.oppdragsgiver}
            </div>
            {kunngjoring.tilbudsfrist && (
              <div>
                <span className="font-medium">Frist:</span>{' '}
                {kunngjoring.tilbudsfrist.slice(0, 10)}
              </div>
            )}
            {kunngjoring.estimert_verdi != null && (
              <div>
                <span className="font-medium">Estimert verdi:</span>{' '}
                {new Intl.NumberFormat('nb-NO').format(kunngjoring.estimert_verdi)} NOK
              </div>
            )}
            {kunngjoring.cpv_koder?.length && (
              <div>
                <span className="font-medium">CPV:</span>{' '}
                {kunngjoring.cpv_koder.join(', ')}
              </div>
            )}
            {kunngjoring.nuts_region && (
              <div>
                <span className="font-medium">Region:</span> {kunngjoring.nuts_region}
              </div>
            )}
          </div>

          <div className="mt-4">
            <button
              onClick={handleKjørSjekk}
              disabled={running}
              className="px-5 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#1F3A5F' }}
            >
              {running ? 'Kjører sjekk...' : 'Kjør GO/NO-GO sjekk'}
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {/* Sjekk result */}
      {sjekk && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <div className="flex items-center gap-3 mb-4">
            <ResultatBadge resultat={sjekk.resultat} />
            <span className="text-sm text-gray-500">Basert på FOA kap. 16</span>
          </div>

          {sjekk.diskvalifiserende.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-semibold text-red-700 uppercase mb-1">
                Diskvalifiserende
              </p>
              <ul className="space-y-1 text-sm text-red-700">
                {sjekk.diskvalifiserende.map((d, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span>🚫</span> {d}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {sjekk.mangler.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-semibold text-yellow-700 uppercase mb-1">
                Mangler / Forbeholdet
              </p>
              <ul className="space-y-1 text-sm text-yellow-700">
                {sjekk.mangler.map((m, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span>⚠️</span> {m}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {sjekk.rule_hits.length > 0 && (
            <details className="mt-3">
              <summary className="text-xs font-semibold uppercase cursor-pointer text-gray-500">
                FOA-regelgrunnlag ({sjekk.rule_hits.length} regler)
              </summary>
              <ul className="mt-2 space-y-2">
                {sjekk.rule_hits.map((r, i) => (
                  <li key={i} className="text-xs text-gray-600">
                    <span className="font-semibold text-gray-800">{r.regel}</span> —{' '}
                    {r.beskrivelse}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}

      {/* SSA-velger */}
      {kunngjoring && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <h2 className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
            SSA-avtaletype
          </h2>
          <div className="flex gap-2 flex-wrap mb-4">
            {SSA_TYPES.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedSsa(type)}
                className="px-3 py-1 rounded-lg text-xs font-semibold border transition-colors"
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
              <div className="flex items-center gap-3 mb-2">
                <span className="font-semibold text-sm">{ssaInfo.navn}</span>
                <span
                  className="px-2 py-0.5 rounded text-xs font-semibold"
                  style={{
                    background:
                      ssaInfo.risiko_nivå === 'HØY'
                        ? '#fee2e2'
                        : ssaInfo.risiko_nivå === 'MIDDELS-HØY'
                          ? '#fef3c7'
                          : ssaInfo.risiko_nivå === 'MIDDELS'
                            ? '#dbeafe'
                            : '#d1fae5',
                    color:
                      ssaInfo.risiko_nivå === 'HØY'
                        ? '#991b1b'
                        : ssaInfo.risiko_nivå === 'MIDDELS-HØY'
                          ? '#92400e'
                          : ssaInfo.risiko_nivå === 'MIDDELS'
                            ? '#1e40af'
                            : '#065f46',
                  }}
                >
                  Risiko: {ssaInfo.risiko_nivå}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{ssaInfo.beskrivelse}</p>

              <div className="mb-3">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-1">
                  Viktige risikoer
                </p>
                <ul className="space-y-1 text-sm text-gray-700">
                  {ssaInfo.risiko.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-1">
                  Obligatoriske bilag
                </p>
                <ul className="space-y-1 text-sm text-gray-700">
                  {ssaInfo.bilag.map((b, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-green-600 mt-0.5">✓</span> {b}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ESPD guide */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
          ESPD-guide — Europeisk egenerklæring
        </h2>
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

      {/* Vanlige feil */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
          10 vanlige feil å unngå
        </h2>
        <ol className="space-y-2">
          {VANLIGE_FEIL.map((feil, i) => (
            <li key={i} className="flex gap-3 text-sm text-gray-700">
              <span
                className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                style={{ background: '#1F3A5F' }}
              >
                {i + 1}
              </span>
              {feil}
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
