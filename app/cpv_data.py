# Felles CPV-data brukt på tvers av alle sider

CPV_GRUPPER: dict[str, list[str]] = {
    "IT og digitalisering": [
        "72000000 — IT-tjenester",
        "72200000 — Programmering og rådgivning",
        "72300000 — Datatjenester",
        "72500000 — Drift og vedlikehold av IT",
        "72600000 — IT-støttetjenester",
        "48000000 — Programvare og systemer",
    ],
    "Bygg og anlegg": [
        "45000000 — Bygge- og anleggsarbeider",
        "45100000 — Grunnarbeider",
        "45200000 — Bygg og konstruksjon",
        "45300000 — Elektro, rør og VVS",
        "45400000 — Overflatearbeider og innredning",
    ],
    "Helse og omsorg": [
        "85000000 — Helse- og sosialtjenester",
        "85100000 — Helsetjenester",
        "85300000 — Sosialtjenester",
        "85320000 — Sosiale velferdstjenester",
    ],
    "Konsulentjenester": [
        "71000000 — Arkitekt- og ingeniørtjenester",
        "73000000 — FoU og rådgivning",
        "79000000 — Forretningstjenester",
        "79100000 — Juridiske tjenester",
        "79200000 — Regnskapstjenester",
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
    ],
    "Opplæring og kurs": [
        "80000000 — Undervisnings- og opplæringstjenester",
        "80300000 — Høyere utdanning",
        "80500000 — Opplæringstjenester",
    ],
}


def cpv_kode(s: str) -> str:
    """Hent CPV-kode fra streng av typen '72000000 — IT-tjenester'."""
    return s.split(" ")[0]


def alle_oppslag() -> dict[str, str]:
    """Returner {visningsnavn: kode} for alle CPV-koder."""
    return {s: cpv_kode(s) for gruppe in CPV_GRUPPER.values() for s in gruppe}
