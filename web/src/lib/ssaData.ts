export interface SsaType {
  navn: string
  risiko_nivå: string
  beskrivelse: string
  risiko: string[]
  bilag: string[]
}

export const SSA_MAP: Record<string, SsaType> = {
  'SSA-B': {
    navn: 'SSA-B Bistandsavtalen (2024)',
    risiko_nivå: 'LAV',
    beskrivelse:
      'Leverandøren leverer innsats — kunden bærer resultatansvaret.',
    risiko: [
      'Bytte av konsulent krever godkjenning fra kunden (Bilag 1).',
      'Timeføring og rapportering er leverandørens ansvar.',
    ],
    bilag: [
      'Bilag 1 — Spesifikasjon av bistanden utfylt',
      'Bilag 2 — Priser per rolle/time',
    ],
  },
  'SSA-T': {
    navn: 'SSA-T Utviklings- og tilpasningsavtalen (2024)',
    risiko_nivå: 'HØY',
    beskrivelse:
      'Leverandøren har fullt resultatansvar for leveransen.',
    risiko: [
      'Ansvarlig ved mislighold fra underleverandører, inkl. standardprogramvare.',
      'Kravspesifikasjon i Bilag 1 er bindende — sørg for at den er komplett.',
      'Forsinkelse kan gi dagbøter — sjekk Bilag 3 fremdriftsplan nøye.',
    ],
    bilag: [
      'Bilag 1 — Kravspesifikasjon besvart punkt for punkt',
      'Bilag 2 — Pris og betalingsplan',
      'Bilag 3 — Fremdriftsplan med milepæler',
      'Bilag 5 — Testplan',
      'Bilag 7 — Underleverandørliste + ESPD per underleverandør',
    ],
  },
  'SSA-D': {
    navn: 'SSA-D Driftsavtalen (2024)',
    risiko_nivå: 'MIDDELS-HØY',
    beskrivelse:
      'Kontinuerlig leveranse med SLA-forpliktelse og servicekreditter.',
    risiko: [
      'SLA-brudd utløser servicekreditter — forhandles i Bilag 3.',
      'Avviklingsplan (exit) er kritisk — hva skjer med data ved oppsigelse?',
      'ISO 27001 kreves ofte — sjekk kravspesifikasjonen.',
      'Datarettigheter er revidert mars 2026 — les DFØs veileder.',
    ],
    bilag: [
      'Bilag 1 — Tjenestebeskrivelse og SLA-nivåer',
      'Bilag 3 — Servicekreditter (rutine ved SLA-brudd)',
      'Bilag 4 — Sikkerhet og personvern (GDPR)',
      'Bilag 5 — Avviklingsplan (exit-plan)',
      'ISO 27001-sertifikat (hvis kravspesifikasjonen krever det)',
    ],
  },
  'SSA-S': {
    navn: 'SSA-S Smidig-avtalen (2024)',
    risiko_nivå: 'MIDDELS',
    beskrivelse:
      'Agile/Scrum med delt resultatansvar — kunden prioriterer backlog.',
    risiko: [
      'Kunden har ansvar for backlog og prioritering.',
      'Definer tydelig hva «ferdig» betyr per sprint i Bilag 1.',
    ],
    bilag: [
      'Bilag 1 — Rammer og mål for oppdraget',
      'Referanser på agile prosjekter (Scrum/Kanban)',
      'Metodebeskrivelse: sprintlengde, retrospektiv, rapportering',
    ],
  },
  'SSA-R': {
    navn: 'SSA-R Rammeavtalen (2015)',
    risiko_nivå: 'LAV-MIDDELS',
    beskrivelse:
      'Rammeavtale med avrop — betaling kun ved faktiske avrop.',
    risiko: [
      'Varsel ved 80 % utnyttelse av rammens totalverdi.',
      'Avropsprosedyren i Bilag 3 er juridisk bindende.',
    ],
    bilag: [
      'Bilag 1 — Rammeavtalens omfang og avgrensning',
      'Bilag 2 — Priser for avrop (prisoversikt per enhet/time)',
      'Bilag 3 — Avropsprosedyre',
    ],
  },
  'SSA-K': {
    navn: 'SSA-K Kjøpsavtalen',
    risiko_nivå: 'LAV',
    beskrivelse:
      'Engangskjøp av produkter eller standardprogramvare.',
    risiko: [
      'Leveringstidspunkt og garantivilkår er de viktigste forhandlingspunktene.',
    ],
    bilag: [
      'Produktspesifikasjon / teknisk dokumentasjon',
      'Leveringstid og garantivilkår',
    ],
  },
}

export const SSA_TYPES = Object.keys(SSA_MAP) as Array<keyof typeof SSA_MAP>

/**
 * Detect the most likely SSA contract type from CPV codes and title.
 */
export function detectSsa(cpvKoder: string[], tittel = ''): string {
  const t = tittel.toLowerCase()
  if (/smidig|scrum|agil|sprint|kanban/.test(t)) return 'SSA-S'
  if (/drift|forvaltning|support|overvåk|hosting/.test(t)) return 'SSA-D'
  if (/utvikling|programmering|bygg|lage|implementer/.test(t)) return 'SSA-T'
  if (/rammeavtale|avrop|minikonkurranse/.test(t)) return 'SSA-R'
  if (/kjøp|levering|anskaffelse av varer|produkter/.test(t)) return 'SSA-K'

  for (const cpv of cpvKoder) {
    if (/^7250|^7251|^7252|^7253|^7254/.test(cpv)) return 'SSA-D'
    if (/^7220|^7221|^7222|^7223|^7224|^7225/.test(cpv)) return 'SSA-T'
    if (cpv.startsWith('72')) return 'SSA-T'
    if (/^73|^79|^71/.test(cpv)) return 'SSA-B'
  }
  return 'SSA-B'
}
