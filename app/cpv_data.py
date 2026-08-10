# Felles CPV-data brukt på tvers av alle sider

CPV_GRUPPER: dict[str, list[str]] = {
    "IT og digitalisering": [
        "72000000 — IT-tjenester generelt",
        "72200000 — Programmering og rådgivning",
        "72300000 — Datatjenester",
        "72500000 — Drift og vedlikehold av IT",
        "72600000 — IT-støtte og konsulenttjenester",
        "48000000 — Programvare og systemer",
    ],
    "Bygg og anlegg": [
        "45000000 — Bygge- og anleggsarbeider",
        "45100000 — Grunnarbeider og rivingsarbeid",
        "45200000 — Bygging av komplette bygg",
        "45300000 — Bygningsinstallasjonsarbeider",
        "45400000 — Ferdigstilling av bygg",
    ],
    "Helse og omsorg": [
        "85000000 — Helse- og sosialtjenester",
        "85100000 — Helsetjenester",
        "85300000 — Sosiale tjenester",
        "85320000 — Sosiale velferdstjenester",
    ],
    "Konsulentjenester": [
        "71000000 — Arkitekt- og ingeniørtjenester",
        "73000000 — FoU og rådgivning",
        "79000000 — Forretningstjenester",
        "79100000 — Juridiske tjenester",
        "79200000 — Regnskapstjenester",
        "79400000 — Bedriftsrådgivning og ledelseskonsulting",
    ],
    "Transport og logistikk": [
        "60000000 — Transporttjenester",
        "60100000 — Veitransport",
        "60400000 — Lufttransport",
        "63000000 — Spedisjon og lagring",
    ],
    "Renhold og drift": [
        "50000000 — Reparasjon og vedlikehold",
        "90000000 — Kloakk, renovasjon og miljø",
        "90900000 — Renholds- og sanitærtjenester",
        "90910000 — Renholdstjenester",
    ],
    "Varer og utstyr": [
        "30000000 — Kontormaskiner og -utstyr",
        "31000000 — Elektrisk utstyr",
        "32000000 — Radio, TV og telekomutstyr",
        "33000000 — Medisinsk og lab-utstyr",
        "34000000 — Transportutstyr og -midler",
    ],
    "Opplæring og kurs": [
        "80000000 — Undervisnings- og opplæringstjenester",
        "80300000 — Høyere utdanning",
        "80500000 — Opplæringstjenester",
    ],
    "Facility management": [
        "70000000 — Eiendomstjenester",
        "70100000 — Eiendomsforvaltning",
        "70300000 — Eiendomsforvaltning på vegne av andre",
        "50700000 — Reparasjon og vedlikehold av bygningsinstallasjoner",
    ],
}

NUTS_REGIONER: dict[str, str] = {
    "Hele Norge": "",
    "Oslo (NO011)": "NO011",
    "Akershus (NO012)": "NO012",
    "Hedmark (NO021)": "NO021",
    "Oppland (NO022)": "NO022",
    "Østfold (NO031)": "NO031",
    "Buskerud (NO032)": "NO032",
    "Vestfold (NO033)": "NO033",
    "Telemark (NO034)": "NO034",
    "Aust-Agder (NO041)": "NO041",
    "Vest-Agder (NO042)": "NO042",
    "Rogaland (NO043)": "NO043",
    "Hordaland (NO051)": "NO051",
    "Vestland (NO052)": "NO052",
    "Møre og Romsdal (NO060)": "NO060",
    "Trøndelag (NO070)": "NO070",
    "Nordland (NO071)": "NO071",
    "Troms (NO072)": "NO072",
    "Finnmark (NO073)": "NO073",
}

SERTIFISERINGER_LISTE: list[str] = [
    "ISO 9001 (kvalitetsstyring)",
    "ISO 14001 (miljøstyring)",
    "ISO 27001 (informasjonssikkerhet)",
    "Miljøfyrtørn",
    "HMS-kort (Arbeidstilsynet)",
    "Startbank-godkjent",
    "Achilles-registrert",
    "Stami-godkjent",
    "GDPR-samsvar dokumentert",
]

DOKUMENT_KATEGORIER: dict[str, str] = {
    "hms_erklæring": "HMS-erklæring (§5 HMS-forskriften)",
    "skatteattest": "Skatteattester (Skatteetaten + kommunen)",
    "firmaattest": "Firmaattest fra Brønnøysund",
    "forsikringsbevis": "Forsikringsbevis",
    "årsregnskap": "Årsregnskap (siste 2 år)",
    "iso_sertifikat": "ISO-sertifikat",
    "hms_kort": "HMS-kort",
    "egenerklæring": "Etisk egenerklæring",
    "egenerklæring_russland": "Egenerklæring russiske selskaper (FOA §24-2)",
    "annet": "Annet dokument",
}

DOKUMENT_UTLOEP_MÅNEDER: dict[str, int | None] = {
    "skatteattest": 6,
    "firmaattest": 3,
    "forsikringsbevis": 12,
    "årsregnskap": 24,
    "iso_sertifikat": 36,
    "hms_kort": 24,
    "hms_erklæring": None,
    "egenerklæring": None,
    "egenerklæring_russland": None,
    "annet": None,
}

SSA_MAP: dict[str, dict] = {
    "SSA-B": {
        "navn": "SSA-B Bistandsavtalen (2024)",
        "risiko_nivå": "LAV",
        "beskrivelse": "Leverandøren leverer innsats — kunden bærer resultatansvaret.",
        "risiko": [
            "ℹ️ Bytte av konsulent krever godkjenning fra kunden (Bilag 1).",
            "ℹ️ Timeføring og rapportering er leverandørens ansvar.",
        ],
        "bilag": [
            "Bilag 1 — Spesifikasjon av bistanden utfylt",
            "Bilag 2 — Priser per rolle/time",
        ],
    },
    "SSA-T": {
        "navn": "SSA-T Utviklings- og tilpasningsavtalen (2024)",
        "risiko_nivå": "HØY",
        "beskrivelse": "Leverandøren har fullt resultatansvar for leveransen.",
        "risiko": [
            "⚠️ Ansvarlig ved mislighold fra underleverandører, inkl. standardprogramvare.",
            "⚠️ Kravspesifikasjon i Bilag 1 er bindende — sørg for at den er komplett.",
            "⚠️ Forsinkelse kan gi dagbøter — sjekk Bilag 3 fremdriftsplan nøye.",
        ],
        "bilag": [
            "Bilag 1 — Kravspesifikasjon besvart punkt for punkt",
            "Bilag 2 — Pris og betalingsplan",
            "Bilag 3 — Fremdriftsplan med milepæler",
            "Bilag 5 — Testplan",
            "Bilag 7 — Underleverandørliste + ESPD per underleverandør",
        ],
    },
    "SSA-D": {
        "navn": "SSA-D Driftsavtalen (2024)",
        "risiko_nivå": "MIDDELS-HØY",
        "beskrivelse": "Kontinuerlig leveranse med SLA-forpliktelse og servicekreditter.",
        "risiko": [
            "⚠️ SLA-brudd utløser servicekreditter — forhandles i Bilag 3.",
            "⚠️ Avviklingsplan (exit) er kritisk — hva skjer med data ved oppsigelse?",
            "⚠️ ISO 27001 kreves ofte — sjekk kravspesifikasjonen.",
            "⚠️ Datarettigheter er revidert mars 2026 — les DFØs veileder.",
        ],
        "bilag": [
            "Bilag 1 — Tjenestebeskrivelse og SLA-nivåer",
            "Bilag 3 — Servicekreditter (rutine ved SLA-brudd)",
            "Bilag 4 — Sikkerhet og personvern (GDPR)",
            "Bilag 5 — Avviklingsplan (exit-plan)",
            "ISO 27001-sertifikat (hvis kravspesifikasjonen krever det)",
        ],
    },
    "SSA-S": {
        "navn": "SSA-S Smidig-avtalen (2024)",
        "risiko_nivå": "MIDDELS",
        "beskrivelse": "Agile/Scrum med delt resultatansvar — kunden prioriterer backlog.",
        "risiko": [
            "ℹ️ Kunden har ansvar for backlog og prioritering.",
            "⚠️ Definer tydelig hva «ferdig» betyr per sprint i Bilag 1.",
        ],
        "bilag": [
            "Bilag 1 — Rammer og mål for oppdraget",
            "Referanser på agile prosjekter (Scrum/Kanban)",
            "Metodebeskrivelse: sprintlengde, retrospektiv, rapportering",
        ],
    },
    "SSA-R": {
        "navn": "SSA-R Rammeavtalen (2015)",
        "risiko_nivå": "LAV-MIDDELS",
        "beskrivelse": "Rammeavtale med avrop — betaling kun ved faktiske avrop.",
        "risiko": [
            "ℹ️ Varsel ved 80 % utnyttelse av rammens totalverdi.",
            "ℹ️ Avropsprosedyren i Bilag 3 er juridisk bindende.",
        ],
        "bilag": [
            "Bilag 1 — Rammeavtalens omfang og avgrensning",
            "Bilag 2 — Priser for avrop (prisoversikt per enhet/time)",
            "Bilag 3 — Avropsprosedyre",
        ],
    },
    "SSA-K": {
        "navn": "SSA-K Kjøpsavtalen",
        "risiko_nivå": "LAV",
        "beskrivelse": "Engangskjøp av produkter eller standardprogramvare.",
        "risiko": [
            "ℹ️ Leveringstidspunkt og garantivilkår er de viktigste forhandlingspunktene.",
        ],
        "bilag": [
            "Produktspesifikasjon / teknisk dokumentasjon",
            "Leveringstid og garantivilkår",
        ],
    },
}


def detect_ssa(cpv_koder: list[str], tittel: str = "") -> str:
    """Returner sannsynlig SSA-type basert på CPV-koder og tittelord."""
    tittel_l = tittel.lower()
    if any(w in tittel_l for w in ["smidig", "scrum", "agil", "sprint", "kanban"]):
        return "SSA-S"
    if any(w in tittel_l for w in ["drift", "forvaltning", "support", "overvåk", "hosting"]):
        return "SSA-D"
    if any(w in tittel_l for w in ["utvikling", "programmering", "bygg", "lage", "implementer"]):
        return "SSA-T"
    if any(w in tittel_l for w in ["rammeavtale", "avrop", "minikonkurranse"]):
        return "SSA-R"
    if any(w in tittel_l for w in ["kjøp", "levering", "anskaffelse av varer", "produkter"]):
        return "SSA-K"
    for cpv in cpv_koder:
        if any(cpv.startswith(p) for p in ("7250", "7251", "7252", "7253", "7254")):
            return "SSA-D"
        if any(cpv.startswith(p) for p in ("7220", "7221", "7222", "7223", "7224", "7225")):
            return "SSA-T"
        if cpv.startswith("72"):
            return "SSA-T"
        if any(cpv.startswith(p) for p in ("73", "79", "71")):
            return "SSA-B"
    return "SSA-B"


def cpv_kode(s: str) -> str:
    """Hent CPV-kode fra streng av typen '72000000 — IT-tjenester'."""
    return s.split(" ")[0]


def alle_oppslag() -> dict[str, str]:
    """Returner {visningsnavn: kode} for alle CPV-koder."""
    return {s: cpv_kode(s) for gruppe in CPV_GRUPPER.values() for s in gruppe}
