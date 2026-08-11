export const CPV_GRUPPER: Record<string, string[]> = {
  'IT og digitalisering': [
    '72000000 — IT-tjenester generelt',
    '72200000 — Programmering og rådgivning',
    '72300000 — Datatjenester',
    '72500000 — Drift og vedlikehold av IT',
    '72600000 — IT-støtte og konsulenttjenester',
    '48000000 — Programvare og systemer',
  ],
  'Bygg og anlegg': [
    '45000000 — Bygge- og anleggsarbeider',
    '45100000 — Grunnarbeider og rivingsarbeid',
    '45200000 — Bygging av komplette bygg',
    '45300000 — Bygningsinstallasjonsarbeider',
    '45400000 — Ferdigstilling av bygg',
  ],
  'Helse og omsorg': [
    '85000000 — Helse- og sosialtjenester',
    '85100000 — Helsetjenester',
    '85300000 — Sosiale tjenester',
    '85320000 — Sosiale velferdstjenester',
  ],
  Konsulentjenester: [
    '71000000 — Arkitekt- og ingeniørtjenester',
    '73000000 — FoU og rådgivning',
    '79000000 — Forretningstjenester',
    '79100000 — Juridiske tjenester',
    '79200000 — Regnskapstjenester',
    '79400000 — Bedriftsrådgivning og ledelseskonsulting',
  ],
  'Transport og logistikk': [
    '60000000 — Transporttjenester',
    '60100000 — Veitransport',
    '60400000 — Lufttransport',
    '63000000 — Spedisjon og lagring',
  ],
  'Renhold og drift': [
    '50000000 — Reparasjon og vedlikehold',
    '90000000 — Kloakk, renovasjon og miljø',
    '90900000 — Renholds- og sanitærtjenester',
    '90910000 — Renholdstjenester',
  ],
  'Varer og utstyr': [
    '30000000 — Kontormaskiner og -utstyr',
    '31000000 — Elektrisk utstyr',
    '32000000 — Radio, TV og telekomutstyr',
    '33000000 — Medisinsk og lab-utstyr',
    '34000000 — Transportutstyr og -midler',
  ],
  'Opplæring og kurs': [
    '80000000 — Undervisnings- og opplæringstjenester',
    '80300000 — Høyere utdanning',
    '80500000 — Opplæringstjenester',
  ],
  'Facility management': [
    '70000000 — Eiendomstjenester',
    '70100000 — Eiendomsforvaltning',
    '70300000 — Eiendomsforvaltning på vegne av andre',
    '50700000 — Reparasjon og vedlikehold av bygningsinstallasjoner',
  ],
}

export const NUTS_REGIONER: Record<string, string> = {
  'Hele Norge': '',
  'Oslo (NO011)': 'NO011',
  'Akershus (NO012)': 'NO012',
  'Hedmark (NO021)': 'NO021',
  'Oppland (NO022)': 'NO022',
  'Østfold (NO031)': 'NO031',
  'Buskerud (NO032)': 'NO032',
  'Vestfold (NO033)': 'NO033',
  'Telemark (NO034)': 'NO034',
  'Aust-Agder (NO041)': 'NO041',
  'Vest-Agder (NO042)': 'NO042',
  'Rogaland (NO043)': 'NO043',
  'Hordaland (NO051)': 'NO051',
  'Vestland (NO052)': 'NO052',
  'Møre og Romsdal (NO060)': 'NO060',
  'Trøndelag (NO070)': 'NO070',
  'Nordland (NO071)': 'NO071',
  'Troms (NO072)': 'NO072',
  'Finnmark (NO073)': 'NO073',
}

/** Extract CPV code from display string like "72000000 — IT-tjenester" */
export function cpvKode(s: string): string {
  return s.split(' ')[0]
}

/** All CPV display strings flattened */
export function alleCpvStrings(): string[] {
  return Object.values(CPV_GRUPPER).flat()
}
