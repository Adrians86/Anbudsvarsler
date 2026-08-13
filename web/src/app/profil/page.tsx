'use client'

import { useState, useEffect, useCallback } from 'react'
import SectionHeader from '@/components/SectionHeader'
import {
  fetchProfil,
  createProfil,
  updateProfil,
  fetchDokumenter,
  createDokument,
  updateDokument,
  deleteDokument,
  fetchReferanser,
  createReferanse,
  deleteReferanse,
} from '@/lib/api'
import type { LeverandorProfil, FirmaDokument, ReferanseProsjekt } from '@/lib/types'
import { useProfile } from '@/hooks/useProfile'
import {
  CPV_GRUPPER,
  NUTS_REGIONER,
  cpvKode,
  SERTIFISERINGER_LISTE,
  DOKUMENT_KATEGORIER,
  DOKUMENT_UTLOEP_MÅNEDER,
} from '@/lib/cpvData'

type Tab = 'firmadata' | 'bransjeprofil' | 'sertifiseringer' | 'referanser' | 'dokumenter'

const KONTRAKT_PREF = [
  { value: 'begge', label: 'Begge typer' },
  { value: 'rammeavtale', label: 'Rammeavtaler' },
  { value: 'enkelt', label: 'Enkeltkontrakter' },
]

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

function expiryLabel(dok: FirmaDokument): string {
  if (!dok.lastet_opp) return 'Ikke lastet opp'
  if (!dok.utloep_dato) return 'Lastet opp'
  const dager = Math.floor(
    (new Date(dok.utloep_dato).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  )
  if (dager < 0) return `UTLØPT (${Math.abs(dager)} dager siden)`
  if (dager <= 30) return `Utløper om ${dager} dager`
  return `Gyldig til ${dok.utloep_dato.slice(0, 10)}`
}

// Build a lookup: cpv display string → cpv code
function buildCpvLookup(): Record<string, string> {
  const lookup: Record<string, string> = {}
  for (const koder of Object.values(CPV_GRUPPER)) {
    for (const k of koder) {
      lookup[k] = cpvKode(k)
    }
  }
  return lookup
}
const CPV_LOOKUP = buildCpvLookup()

export default function ProfilPage() {
  const { profilId, setProfilId, loaded } = useProfile()
  const [activeTab, setActiveTab] = useState<Tab>('firmadata')

  // Profil state
  const [profil, setProfil] = useState<Partial<LeverandorProfil>>({
    cpv_koder: [],
    nuts_regioner: [],
    sertifiseringer: [],
  })
  const [profilLoading, setProfilLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveMsg, setSaveMsg] = useState<{ ok: boolean; text: string } | null>(null)

  // Brreg lookup
  const [brregLoading, setBrregLoading] = useState(false)
  const [brregError, setBrregError] = useState<string | null>(null)

  // Dokumenter
  const [dokumenter, setDokumenter] = useState<FirmaDokument[]>([])
  const [dokLoading, setDokLoading] = useState(false)
  const [dokSaving, setDokSaving] = useState(false)

  // Nytt dokument form
  const [nyDokKat, setNyDokKat] = useState(Object.keys(DOKUMENT_KATEGORIER)[0])
  const [nyDokTittel, setNyDokTittel] = useState('')
  const [nyDokUtloep, setNyDokUtloep] = useState('')
  const [nyDokOpp, setNyDokOpp] = useState(false)

  // Referanser
  const [referanser, setReferanser] = useState<ReferanseProsjekt[]>([])
  const [refLoading, setRefLoading] = useState(false)
  const [refForm, setRefForm] = useState({
    prosjektnavn: '',
    oppdragsgiver_navn: '',
    oppdragsgiver_org_nr: '',
    kontraktsverdi_nok: '',
    periode_fra: '',
    periode_til: '',
    cpv: '',
    kontaktperson: '',
    kontakttelefon: '',
    beskrivelse: '',
    kan_kontaktes: true,
  })
  const [refSaving, setRefSaving] = useState(false)
  const [showRefForm, setShowRefForm] = useState(false)

  // Load profil on mount
  useEffect(() => {
    if (!loaded || !profilId) return
    setProfilLoading(true)
    fetchProfil(profilId)
      .then((p) => setProfil(p))
      .catch(() => { /* use empty defaults */ })
      .finally(() => setProfilLoading(false))
  }, [loaded, profilId])

  // Load dokumenter when tab active
  const loadDokumenter = useCallback(async () => {
    if (!profilId) return
    setDokLoading(true)
    try {
      setDokumenter(await fetchDokumenter(profilId))
    } catch { /* ignore */ }
    finally { setDokLoading(false) }
  }, [profilId])

  const loadReferanser = useCallback(async () => {
    if (!profilId) return
    setRefLoading(true)
    try {
      setReferanser(await fetchReferanser(profilId))
    } catch { /* ignore */ }
    finally { setRefLoading(false) }
  }, [profilId])

  useEffect(() => {
    if (activeTab === 'dokumenter') loadDokumenter()
    if (activeTab === 'referanser') loadReferanser()
  }, [activeTab, loadDokumenter, loadReferanser])

  // ── Field helpers ─────────────────────────────────────────────────────────────

  function setField<K extends keyof LeverandorProfil>(key: K, value: LeverandorProfil[K]) {
    setProfil((prev) => ({ ...prev, [key]: value }))
  }

  // ── Brreg lookup ──────────────────────────────────────────────────────────────

  async function handleBrregLookup() {
    const clean = (profil.org_nr ?? '').replace(/\D/g, '')
    if (clean.length !== 9) {
      setBrregError('Oppgi et gyldig 9-sifret organisasjonsnummer.')
      return
    }
    setBrregLoading(true)
    setBrregError(null)
    try {
      const res = await fetch(`https://data.brreg.no/enhetsregisteret/api/enheter/${clean}`)
      if (!res.ok) throw new Error('Ikke funnet')
      const data = await res.json()
      const adr = data.forretningsadresse ?? {}
      setProfil((prev) => ({
        ...prev,
        org_nr: clean,
        navn: data.navn ?? prev.navn,
        organisasjonsform: data.organisasjonsform?.beskrivelse ?? prev.organisasjonsform,
        adresse: (adr.adresse ?? []).join(', ') || prev.adresse,
        postnr: String(adr.postnummer ?? '') || prev.postnr,
        sted: adr.poststed ?? prev.sted,
        antall_ansatte: data.antallAnsatte ?? prev.antall_ansatte,
      }))
    } catch {
      setBrregError('Organisasjonsnummeret ble ikke funnet i Brønnøysundregisteret.')
    } finally {
      setBrregLoading(false)
    }
  }

  // ── Save helpers ──────────────────────────────────────────────────────────────

  function showSave(ok: boolean, text: string) {
    setSaveMsg({ ok, text })
    setTimeout(() => setSaveMsg(null), 3000)
  }

  async function saveFirmadata(e: React.FormEvent) {
    e.preventDefault()
    if (!profil.org_nr || !profil.navn) {
      showSave(false, 'Organisasjonsnummer og firmanavn er obligatorisk.')
      return
    }
    setSaving(true)
    try {
      const payload = {
        ...profil,
        cpv_koder: profil.cpv_koder ?? [],
        nuts_regioner: profil.nuts_regioner ?? [],
        sertifiseringer: profil.sertifiseringer ?? [],
      }
      if (profilId) {
        const updated = await updateProfil(profilId, payload)
        setProfil(updated)
      } else {
        const created = await createProfil(payload)
        setProfil(created)
        setProfilId(created.id)
      }
      showSave(true, 'Firmadata lagret!')
    } catch (err) {
      showSave(false, err instanceof Error ? err.message : 'Feil ved lagring')
    } finally {
      setSaving(false)
    }
  }

  async function saveBransjeprofil(e: React.FormEvent) {
    e.preventDefault()
    if (!profilId) {
      showSave(false, 'Lagre firmadata i Tab 1 først for å opprette profilen.')
      return
    }
    setSaving(true)
    try {
      const updated = await updateProfil(profilId, {
        ...profil,
        cpv_koder: profil.cpv_koder ?? [],
        nuts_regioner: profil.nuts_regioner ?? [],
        sertifiseringer: profil.sertifiseringer ?? [],
      })
      setProfil(updated)
      showSave(true, 'Bransjeprofil lagret!')
    } catch (err) {
      showSave(false, err instanceof Error ? err.message : 'Feil ved lagring')
    } finally {
      setSaving(false)
    }
  }

  async function saveSertifiseringer(e: React.FormEvent) {
    e.preventDefault()
    if (!profilId) {
      showSave(false, 'Lagre firmadata i Tab 1 først.')
      return
    }
    setSaving(true)
    try {
      const updated = await updateProfil(profilId, {
        ...profil,
        cpv_koder: profil.cpv_koder ?? [],
        nuts_regioner: profil.nuts_regioner ?? [],
        sertifiseringer: profil.sertifiseringer ?? [],
      })
      setProfil(updated)
      showSave(true, 'Sertifiseringer lagret!')
    } catch (err) {
      showSave(false, err instanceof Error ? err.message : 'Feil ved lagring')
    } finally {
      setSaving(false)
    }
  }

  // ── CPV toggle ────────────────────────────────────────────────────────────────

  function toggleCpv(displayString: string) {
    const kode = CPV_LOOKUP[displayString]
    if (!kode) return
    const current = profil.cpv_koder ?? []
    if (current.includes(kode)) {
      setField('cpv_koder', current.filter((c) => c !== kode))
    } else {
      setField('cpv_koder', [...current, kode])
    }
  }

  function toggleNuts(label: string) {
    const kode = NUTS_REGIONER[label]
    const current = profil.nuts_regioner ?? []
    if (kode === '') {
      // "Hele Norge" — toggle all
      if (current.length === 0) return
      setField('nuts_regioner', [])
    } else if (current.includes(kode)) {
      setField('nuts_regioner', current.filter((c) => c !== kode))
    } else {
      setField('nuts_regioner', [...current, kode])
    }
  }

  function toggleSert(s: string) {
    const current = profil.sertifiseringer ?? []
    if (current.includes(s)) {
      setField('sertifiseringer', current.filter((x) => x !== s))
    } else {
      setField('sertifiseringer', [...current, s])
    }
  }

  // ── Dokument actions ──────────────────────────────────────────────────────────

  async function handleMarkertOpp(dokId: number, utloepDato?: string) {
    setDokSaving(true)
    try {
      const updated = await updateDokument(dokId, {
        lastet_opp: true,
        ...(utloepDato ? { utloep_dato: utloepDato } : {}),
      })
      setDokumenter((prev) => prev.map((d) => (d.id === dokId ? updated : d)))
    } catch { /* ignore */ }
    finally { setDokSaving(false) }
  }

  async function handleSlettDok(dokId: number) {
    if (!confirm('Slett dokument?')) return
    try {
      await deleteDokument(dokId)
      setDokumenter((prev) => prev.filter((d) => d.id !== dokId))
    } catch { /* ignore */ }
  }

  async function handleOpprettStandardsett() {
    if (!profilId) return
    setDokSaving(true)
    try {
      const eksistKat = new Set(dokumenter.map((d) => d.kategori))
      const nyeDok: FirmaDokument[] = []
      for (const [kat, tittel] of Object.entries(DOKUMENT_KATEGORIER)) {
        if (eksistKat.has(kat)) continue
        const mnd = DOKUMENT_UTLOEP_MÅNEDER[kat]
        const utloep = mnd
          ? new Date(Date.now() + mnd * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
          : undefined
        const dok = await createDokument({
          profil_id: profilId,
          kategori: kat,
          tittel,
          lastet_opp: false,
          utloep_dato: utloep,
        })
        nyeDok.push(dok)
      }
      setDokumenter((prev) => [...prev, ...nyeDok])
    } catch { /* ignore */ }
    finally { setDokSaving(false) }
  }

  async function handleNyttDokument(e: React.FormEvent) {
    e.preventDefault()
    if (!profilId) return
    setDokSaving(true)
    try {
      const dok = await createDokument({
        profil_id: profilId,
        kategori: nyDokKat,
        tittel: nyDokTittel || DOKUMENT_KATEGORIER[nyDokKat],
        lastet_opp: nyDokOpp,
        utloep_dato: nyDokUtloep || undefined,
      })
      setDokumenter((prev) => [...prev, dok])
      setNyDokTittel('')
      setNyDokUtloep('')
      setNyDokOpp(false)
    } catch { /* ignore */ }
    finally { setDokSaving(false) }
  }

  // ── Referanse actions ─────────────────────────────────────────────────────────

  async function handleLeggTilReferanse(e: React.FormEvent) {
    e.preventDefault()
    if (!profilId || !refForm.prosjektnavn || !refForm.oppdragsgiver_navn) {
      showSave(false, 'Prosjektnavn og oppdragsgiver er obligatorisk.')
      return
    }
    setRefSaving(true)
    try {
      const ref = await createReferanse({
        profil_id: profilId,
        prosjektnavn: refForm.prosjektnavn,
        oppdragsgiver_navn: refForm.oppdragsgiver_navn,
        oppdragsgiver_org_nr: refForm.oppdragsgiver_org_nr || undefined,
        kontraktsverdi_nok: refForm.kontraktsverdi_nok
          ? Number(refForm.kontraktsverdi_nok)
          : undefined,
        periode_fra: refForm.periode_fra || undefined,
        periode_til: refForm.periode_til || undefined,
        cpv: refForm.cpv || undefined,
        beskrivelse: refForm.beskrivelse || undefined,
        kontaktperson: refForm.kontaktperson || undefined,
        kontakttelefon: refForm.kontakttelefon || undefined,
        kan_kontaktes: refForm.kan_kontaktes,
      })
      setReferanser((prev) => [...prev, ref])
      setRefForm({
        prosjektnavn: '', oppdragsgiver_navn: '', oppdragsgiver_org_nr: '',
        kontraktsverdi_nok: '', periode_fra: '', periode_til: '', cpv: '',
        kontaktperson: '', kontakttelefon: '', beskrivelse: '', kan_kontaktes: true,
      })
      setShowRefForm(false)
    } catch (err) {
      showSave(false, err instanceof Error ? err.message : 'Feil')
    } finally {
      setRefSaving(false)
    }
  }

  async function handleSlettReferanse(refId: number) {
    if (!confirm('Slett referanseprosjekt?')) return
    try {
      await deleteReferanse(refId)
      setReferanser((prev) => prev.filter((r) => r.id !== refId))
    } catch { /* ignore */ }
  }

  if (!loaded) return null

  const tabs: { key: Tab; label: string }[] = [
    { key: 'firmadata', label: '📋 Firmadata' },
    { key: 'bransjeprofil', label: '🏷️ Bransjeprofil' },
    { key: 'sertifiseringer', label: '✅ Sertifiseringer' },
    { key: 'referanser', label: '📎 Referanser' },
    { key: 'dokumenter', label: '📂 Dokumenter' },
  ]

  return (
    <div>
      <SectionHeader eyebrow="MIN LEVERANDØRPROFIL" title="🏢 Min leverandørprofil" />

      {profilId && (
        <div className="mb-4 text-xs text-gray-400">Profil ID: {profilId}</div>
      )}

      {saveMsg && (
        <div
          className={`mb-4 px-4 py-2 rounded-lg text-sm font-medium ${
            saveMsg.ok
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          {saveMsg.text}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 flex-wrap">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
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

      {/* ── TAB 1: FIRMADATA ─────────────────────────────────────────────────────── */}
      {activeTab === 'firmadata' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          {/* Brreg lookup */}
          <div className="mb-5">
            <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Organisasjonsoppslag
            </p>
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <input
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  placeholder="123456789"
                  value={profil.org_nr ?? ''}
                  onChange={(e) => setField('org_nr', e.target.value)}
                />
              </div>
              <button
                onClick={handleBrregLookup}
                disabled={brregLoading}
                className="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50 shrink-0"
                style={{ background: '#1F3A5F' }}
              >
                {brregLoading ? 'Søker...' : 'Hent fra Brønnøysund'}
              </button>
            </div>
            {brregError && (
              <p className="mt-1 text-xs text-red-600">{brregError}</p>
            )}
          </div>

          <form onSubmit={saveFirmadata}>
            <div className="grid grid-cols-2 gap-x-6 gap-y-4">
              {/* Left column */}
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    Organisasjonsnummer *
                  </label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="123456789"
                    value={profil.org_nr ?? ''}
                    onChange={(e) => setField('org_nr', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Firmanavn *</label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="AS Mitt Firma"
                    value={profil.navn ?? ''}
                    onChange={(e) => setField('navn', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    Organisasjonsform
                  </label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="Aksjeselskap"
                    value={profil.organisasjonsform ?? ''}
                    onChange={(e) => setField('organisasjonsform', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    Antall ansatte
                  </label>
                  <input
                    type="number"
                    min={0}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    value={profil.antall_ansatte ?? ''}
                    onChange={(e) =>
                      setField('antall_ansatte', e.target.value ? Number(e.target.value) : undefined)
                    }
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    Årlig omsetning (NOK)
                    <span className="text-gray-400 ml-1">— brukes i §16-4 finansiell sjekk</span>
                  </label>
                  <input
                    type="number"
                    min={0}
                    step={500000}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    value={profil.aarlig_omsetning_nok ?? ''}
                    onChange={(e) =>
                      setField('aarlig_omsetning_nok', e.target.value ? Number(e.target.value) : undefined)
                    }
                  />
                </div>
              </div>

              {/* Right column */}
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Kontaktperson</label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="Ola Nordmann"
                    value={profil.kontaktperson ?? ''}
                    onChange={(e) => setField('kontaktperson', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">E-post</label>
                  <input
                    type="email"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="post@firma.no"
                    value={profil.epost ?? ''}
                    onChange={(e) => setField('epost', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Telefon</label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="+47 12 34 56 78"
                    value={profil.telefon ?? ''}
                    onChange={(e) => setField('telefon', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Nettsted</label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="https://firma.no"
                    value={profil.nettsted ?? ''}
                    onChange={(e) => setField('nettsted', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Adresse</label>
                  <input
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    placeholder="Storgata 1"
                    value={profil.adresse ?? ''}
                    onChange={(e) => setField('adresse', e.target.value)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Postnummer</label>
                    <input
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                      placeholder="0150"
                      value={profil.postnr ?? ''}
                      onChange={(e) => setField('postnr', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Poststed</label>
                    <input
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                      placeholder="Oslo"
                      value={profil.sted ?? ''}
                      onChange={(e) => setField('sted', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-5 flex gap-3 items-center">
              <button
                type="submit"
                disabled={saving}
                className="px-5 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
                style={{ background: '#1F3A5F' }}
              >
                {saving ? 'Lagrer...' : 'Lagre firmadata'}
              </button>
              {!profilId && (
                <p className="text-xs text-gray-400">
                  Lagring oppretter en ny profil og setter Profil-ID i sessionStorage.
                </p>
              )}
            </div>
          </form>
        </div>
      )}

      {/* ── TAB 2: BRANSJEPROFIL ──────────────────────────────────────────────────── */}
      {activeTab === 'bransjeprofil' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <form onSubmit={saveBransjeprofil}>
            {/* CPV */}
            <p className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
              CPV-koder (hva tilbyr dere?)
            </p>
            <div className="grid grid-cols-2 gap-x-6 gap-y-4 mb-5">
              {Object.entries(CPV_GRUPPER).map(([bransje, koder]) => (
                <div key={bransje}>
                  <p className="text-xs font-semibold text-gray-500 mb-1">{bransje}</p>
                  <div className="space-y-1">
                    {koder.map((displayStr) => {
                      const kode = CPV_LOOKUP[displayStr]
                      const checked = (profil.cpv_koder ?? []).includes(kode)
                      return (
                        <label
                          key={displayStr}
                          className="flex items-center gap-2 text-xs cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => toggleCpv(displayStr)}
                            className="rounded"
                          />
                          {displayStr}
                        </label>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>

            <hr className="my-5 border-gray-100" />

            {/* NUTS */}
            <p className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
              Geografisk dekning (NUTS-regioner)
            </p>
            <div className="grid grid-cols-3 gap-1 mb-5">
              {Object.entries(NUTS_REGIONER).map(([label, kode]) => {
                const checked =
                  kode === ''
                    ? (profil.nuts_regioner ?? []).length === 0
                    : (profil.nuts_regioner ?? []).includes(kode)
                return (
                  <label key={label} className="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleNuts(label)}
                      className="rounded"
                    />
                    {label}
                  </label>
                )
              })}
            </div>

            <hr className="my-5 border-gray-100" />

            {/* Value range + contract preference */}
            <div className="grid grid-cols-3 gap-4 mb-5">
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Min. kontraktsverdi (NOK)
                </label>
                <input
                  type="number"
                  min={0}
                  step={100000}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  value={profil.min_verdi ?? ''}
                  onChange={(e) =>
                    setField('min_verdi', e.target.value ? Number(e.target.value) : undefined)
                  }
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Maks. kontraktsverdi (NOK)
                </label>
                <input
                  type="number"
                  min={0}
                  step={500000}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  value={profil.max_verdi ?? ''}
                  onChange={(e) =>
                    setField('max_verdi', e.target.value ? Number(e.target.value) : undefined)
                  }
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Foretrekker kontraktstype
                </label>
                <select
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
                  value={profil.kontrakt_preferanse ?? 'begge'}
                  onChange={(e) => setField('kontrakt_preferanse', e.target.value)}
                >
                  {KONTRAKT_PREF.map(({ value, label }) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={saving || !profilId}
              className="px-5 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#1F3A5F' }}
            >
              {saving ? 'Lagrer...' : 'Lagre bransjeprofil'}
            </button>
            {!profilId && (
              <p className="mt-2 text-xs text-yellow-600">
                Lagre firmadata i Tab 1 først for å opprette profilen.
              </p>
            )}
          </form>
        </div>
      )}

      {/* ── TAB 3: SERTIFISERINGER ───────────────────────────────────────────────── */}
      {activeTab === 'sertifiseringer' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <form onSubmit={saveSertifiseringer}>
            <p className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
              Velg alle sertifiseringer og godkjenninger dere har
            </p>
            <div className="space-y-2 mb-5">
              {SERTIFISERINGER_LISTE.map((s) => (
                <label key={s} className="flex items-center gap-3 cursor-pointer text-sm">
                  <input
                    type="checkbox"
                    checked={(profil.sertifiseringer ?? []).includes(s)}
                    onChange={() => toggleSert(s)}
                    className="rounded w-4 h-4"
                  />
                  {s}
                </label>
              ))}
            </div>

            <div className="mb-5">
              <label className="block text-xs text-gray-500 mb-1">
                Andre sertifiseringer (komma-separert)
              </label>
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                placeholder="Spesiell bransjesertifisering..."
                value={(profil.sertifiseringer ?? [])
                  .filter((s) => !SERTIFISERINGER_LISTE.includes(s))
                  .join(', ')}
                onChange={(e) => {
                  const andre = e.target.value
                    .split(',')
                    .map((s) => s.trim())
                    .filter(Boolean)
                  const standard = (profil.sertifiseringer ?? []).filter((s) =>
                    SERTIFISERINGER_LISTE.includes(s)
                  )
                  setField('sertifiseringer', [...standard, ...andre])
                }}
              />
            </div>

            <button
              type="submit"
              disabled={saving || !profilId}
              className="px-5 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: '#1F3A5F' }}
            >
              {saving ? 'Lagrer...' : 'Lagre sertifiseringer'}
            </button>
            {!profilId && (
              <p className="mt-2 text-xs text-yellow-600">
                Lagre firmadata i Tab 1 først.
              </p>
            )}
          </form>
        </div>
      )}

      {/* ── TAB 4: REFERANSER ─────────────────────────────────────────────────────── */}
      {activeTab === 'referanser' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          {!profilId ? (
            <p className="text-sm text-yellow-600">Lagre firmadata i Tab 1 først.</p>
          ) : refLoading ? (
            <p className="text-sm text-gray-500 animate-pulse">Laster referanser...</p>
          ) : (
            <>
              <p className="text-sm font-semibold mb-3" style={{ color: '#1F3A5F' }}>
                {referanser.length} referanseprosjekt(er) registrert
              </p>

              {referanser.length === 0 ? (
                <p className="text-sm text-gray-500 mb-4">
                  Ingen referanser registrert ennå. Legg til minst ett (FOA §16-8).
                </p>
              ) : (
                <div className="space-y-3 mb-4">
                  {referanser.map((ref) => (
                    <div
                      key={ref.id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-semibold text-sm">
                            {ref.prosjektnavn}
                          </p>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {ref.oppdragsgiver_navn}
                            {ref.periode_fra && ` · ${ref.periode_fra}–${ref.periode_til ?? ''}`}
                          </p>
                          {ref.kontraktsverdi_nok && (
                            <p className="text-xs text-gray-400 mt-0.5">
                              {new Intl.NumberFormat('nb-NO').format(ref.kontraktsverdi_nok)} NOK
                            </p>
                          )}
                          {ref.beskrivelse && (
                            <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                              {ref.beskrivelse}
                            </p>
                          )}
                          {ref.kontaktperson && (
                            <p className="text-xs text-gray-400 mt-0.5">
                              Kontakt: {ref.kontaktperson}{' '}
                              {ref.kontakttelefon ?? ''}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => handleSlettReferanse(ref.id)}
                          className="text-red-400 hover:text-red-600 text-xs shrink-0"
                          title="Slett"
                        >
                          Slett
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={() => setShowRefForm((v) => !v)}
                className="px-4 py-2 rounded-lg text-sm font-semibold border border-gray-300 bg-white hover:bg-gray-50 mb-4"
              >
                {showRefForm ? 'Skjul skjema' : '+ Legg til nytt referanseprosjekt'}
              </button>

              {showRefForm && (
                <form
                  onSubmit={handleLeggTilReferanse}
                  className="border border-gray-200 rounded-lg p-4 space-y-3"
                >
                  <div className="grid grid-cols-2 gap-3">
                    {(
                      [
                        ['prosjektnavn', 'Prosjektnavn *', 'System-utvikling for NAV'],
                        ['oppdragsgiver_navn', 'Oppdragsgiver *', 'NAV'],
                        ['oppdragsgiver_org_nr', 'Oppdragsgivers org.nr', '889640782'],
                        ['kontraktsverdi_nok', 'Kontraktsverdi (NOK)', ''],
                        ['periode_fra', 'Periode fra', '2023-01'],
                        ['periode_til', 'Periode til', '2024-06'],
                        ['cpv', 'CPV-kode', '72200000'],
                        ['kontaktperson', 'Kontaktperson', 'Kari Nordmann'],
                        ['kontakttelefon', 'Kontakttelefon', '+47 ...'],
                      ] as [keyof typeof refForm, string, string][]
                    ).map(([field, label, placeholder]) => (
                      <div key={field}>
                        <label className="block text-xs text-gray-500 mb-1">{label}</label>
                        <input
                          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                          placeholder={placeholder}
                          value={refForm[field] as string}
                          onChange={(e) =>
                            setRefForm((prev) => ({ ...prev, [field]: e.target.value }))
                          }
                          type={field === 'kontraktsverdi_nok' ? 'number' : 'text'}
                          min={field === 'kontraktsverdi_nok' ? 0 : undefined}
                          required={field === 'prosjektnavn' || field === 'oppdragsgiver_navn'}
                        />
                      </div>
                    ))}
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      Beskrivelse (maks 500 tegn)
                    </label>
                    <textarea
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                      rows={3}
                      maxLength={500}
                      value={refForm.beskrivelse}
                      onChange={(e) =>
                        setRefForm((prev) => ({ ...prev, beskrivelse: e.target.value }))
                      }
                    />
                  </div>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={refForm.kan_kontaktes}
                      onChange={(e) =>
                        setRefForm((prev) => ({ ...prev, kan_kontaktes: e.target.checked }))
                      }
                      className="rounded"
                    />
                    Oppdragsgiver kan kontaktes
                  </label>
                  <button
                    type="submit"
                    disabled={refSaving}
                    className="px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
                    style={{ background: '#1F3A5F' }}
                  >
                    {refSaving ? 'Legger til...' : 'Legg til referanse'}
                  </button>
                </form>
              )}
            </>
          )}
        </div>
      )}

      {/* ── TAB 5: DOKUMENTER ─────────────────────────────────────────────────────── */}
      {activeTab === 'dokumenter' && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          {!profilId ? (
            <p className="text-sm text-yellow-600">Lagre firmadata i Tab 1 først.</p>
          ) : dokLoading ? (
            <p className="text-sm text-gray-500 animate-pulse">Laster dokumenter...</p>
          ) : (
            <>
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-semibold" style={{ color: '#1F3A5F' }}>
                  {dokumenter.length} dokument(er) registrert
                </p>
                <button
                  onClick={handleOpprettStandardsett}
                  disabled={dokSaving}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  {dokSaving ? 'Oppretter...' : 'Opprett standard dokumentsett'}
                </button>
              </div>

              {/* Legend */}
              <div className="mb-4 text-xs text-gray-400">
                ✅ gyldig &nbsp;|&nbsp; 🟡 utløper snart (&lt;30d) &nbsp;|&nbsp; 🔴 utløpt &nbsp;|&nbsp; ⬜ ikke lastet opp
              </div>

              {dokumenter.length > 0 && (
                <div className="space-y-3 mb-5">
                  {dokumenter.map((dok) => (
                    <div
                      key={dok.id}
                      className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg"
                    >
                      <span className="text-xl shrink-0">{expiryIcon(dok)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {dok.tittel ?? DOKUMENT_KATEGORIER[dok.kategori] ?? dok.kategori}
                        </p>
                        <p className="text-xs text-gray-400">{expiryLabel(dok)}</p>
                      </div>
                      <div className="flex gap-2 items-center shrink-0">
                        {!dok.lastet_opp && (
                          <button
                            onClick={() => handleMarkertOpp(dok.id)}
                            disabled={dokSaving}
                            className="px-2 py-1 rounded text-xs font-medium border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50"
                          >
                            Marker opp
                          </button>
                        )}
                        <button
                          onClick={() => handleSlettDok(dok.id)}
                          className="text-xs text-red-400 hover:text-red-600"
                        >
                          Slett
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Nytt dokument */}
              <details>
                <summary className="text-sm font-medium cursor-pointer text-gray-600 mb-3">
                  + Legg til dokument manuelt
                </summary>
                <form
                  onSubmit={handleNyttDokument}
                  className="mt-3 border border-gray-200 rounded-lg p-4 space-y-3"
                >
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Kategori</label>
                    <select
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
                      value={nyDokKat}
                      onChange={(e) => setNyDokKat(e.target.value)}
                    >
                      {Object.entries(DOKUMENT_KATEGORIER).map(([k, v]) => (
                        <option key={k} value={k}>{v}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      Tittel (valgfritt)
                    </label>
                    <input
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                      value={nyDokTittel}
                      onChange={(e) => setNyDokTittel(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      Utløpsdato (valgfritt)
                    </label>
                    <input
                      type="date"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                      value={nyDokUtloep}
                      onChange={(e) => setNyDokUtloep(e.target.value)}
                    />
                  </div>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={nyDokOpp}
                      onChange={(e) => setNyDokOpp(e.target.checked)}
                      className="rounded"
                    />
                    Allerede lastet opp / tilgjengelig
                  </label>
                  <button
                    type="submit"
                    disabled={dokSaving}
                    className="px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
                    style={{ background: '#1F3A5F' }}
                  >
                    {dokSaving ? 'Legger til...' : 'Legg til'}
                  </button>
                </form>
              </details>
            </>
          )}
        </div>
      )}
    </div>
  )
}
