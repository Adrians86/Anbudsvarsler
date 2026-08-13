export interface Kunngjoring {
  id: number
  kilde: string
  ekstern_id: string
  tittel: string
  oppdragsgiver: string
  publisert: string
  url: string
  tilbudsfrist?: string
  estimert_verdi?: number
  cpv_koder?: string[]
  nuts_region?: string
  beskrivelse?: string
}

export interface LeverandorProfil {
  id: number
  org_nr: string
  navn: string
  kontaktperson?: string
  epost?: string
  telefon?: string
  nettsted?: string
  adresse?: string
  postnr?: string
  sted?: string
  organisasjonsform?: string
  antall_ansatte?: number
  aarlig_omsetning_nok?: number
  cpv_koder: string[]
  nuts_regioner: string[]
  min_verdi?: number
  max_verdi?: number
  kontrakt_preferanse?: string
  sertifiseringer: string[]
}

export type VarslingStatus =
  | 'NY'
  | 'SETT'
  | 'INTERESSERT'
  | 'FORKASTET'
  | 'LEVERT'
  | 'VUNNET'
  | 'TAPT'

export interface Varsling {
  id: number
  kunngjoring_id: number
  profil_id: number
  relevans_score: number
  status: VarslingStatus
  tittel?: string
  oppdragsgiver?: string
  tilbudsfrist?: string
  estimert_verdi?: number
  cpv_koder?: string[]
  url?: string
}

export type KvalResultat = 'GO' | 'NO-GO' | 'GÅ VIDERE MED FORBEHOLD'

export interface Kvalifikasjonssjekk {
  id: number
  varsling_id: number
  profil_id: number
  resultat: KvalResultat
  mangler: string[]
  diskvalifiserende: string[]
  rule_hits: { regel: string; beskrivelse: string }[]
}

export interface HealthResponse {
  status: string
  version: string
}

export interface SyncResponse {
  nye_kunngjøringer: number
  nye_varsler: number
  totalt_hentet: number
  doffin: number
  ted: number
}

export interface Bibliotekelement {
  id: number
  profil_id: number
  navn: string
  kategori: string
  innhold?: string
  created_at?: string
}

export interface FirmaDokument {
  id: number
  profil_id: number
  navn?: string
  tittel?: string
  kategori: string
  lastet_opp: boolean
  utloep_dato?: string
  created_at?: string
}

export interface ReferanseProsjekt {
  id: number
  profil_id: number
  prosjektnavn: string
  oppdragsgiver_navn: string
  oppdragsgiver_org_nr?: string
  kontraktsverdi_nok?: number
  periode_fra?: string
  periode_til?: string
  cpv?: string
  beskrivelse?: string
  kontaktperson?: string
  kontakttelefon?: string
  kan_kontaktes?: boolean
}
