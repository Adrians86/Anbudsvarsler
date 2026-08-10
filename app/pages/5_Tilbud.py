"""Side 5 — Tilbudsstøtte: sjekkliste, ESPD og SSA-bilag."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st
from datetime import datetime

from app.config import API_BASE_URL as API_BASE
from app.cpv_data import SSA_MAP, detect_ssa
from app.theme import inject_css, section_header

st.set_page_config(page_title="Tilbud | Anbudsvarsler", page_icon="📋", layout="wide")
inject_css()

section_header("📋 Tilbudsstøtte", eyebrow="TILBUDSSTØTTE")

profil_id = st.session_state.get("profil_id")
if not profil_id:
    st.warning("Du må fylle inn din leverandørprofil på siden **Min profil** først.")
    st.stop()

# Hent varslinger for profilen
try:
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{API_BASE}/varsling", params={"profil_id": profil_id})
        resp.raise_for_status()
        varslinger = resp.json()
except Exception as e:
    st.error(f"Kunne ikke hente varslinger: {e}")
    varslinger = []

if not varslinger:
    st.info("Ingen varslinger funnet. Kjør synkronisering via Admin-siden.")
    st.stop()

varsling_valg = {
    f"{v.get('id')} — {v.get('tittel', 'Ukjent')}": v for v in varslinger
}

valgt_label = st.selectbox("Velg kunngjøring:", options=list(varsling_valg.keys()))
valgt = varsling_valg[valgt_label]
varsling_id = valgt["id"]

# Auto-detekter SSA-type
cpv_koder = valgt.get("cpv_koder") or []
tittel = valgt.get("tittel") or ""
auto_ssa = detect_ssa(cpv_koder, tittel)
ssa_bilag = SSA_MAP.get(auto_ssa, {}).get("bilag", [])

tab_sjekkliste, tab_espd, tab_bilag = st.tabs(["Sjekkliste", "ESPD-guide", "SSA-bilag"])

# ── Tab 1: Sjekkliste ────────────────────────────────────────────
with tab_sjekkliste:
    # Hent eksisterende sjekkliste
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{API_BASE}/sjekkliste/{varsling_id}")
            resp.raise_for_status()
            elementer = resp.json()
    except Exception as e:
        st.error(f"Kunne ikke hente sjekkliste: {e}")
        elementer = []

    st.markdown(f"### Sjekkliste for: {valgt.get('tittel', '')}")

    STANDARD_PUNKTER = [
        "Lese og forstå konkurransegrunnlaget",
        "Sjekke kvalifikasjonskrav (GO/NO-GO)",
        "Hente ut relevante referanser fra biblioteket",
        "Utarbeide prisskjema / tilbudssum",
        "Skaffe attest for skatt og merverdiavgift",
        "Fylle ut og signere ESPD",
        "Signere og sende inn tilbud innen fristen",
    ]
    # Legg til SSA-spesifikke punkter
    SSA_PUNKTER = [f"[{auto_ssa}] {b}" for b in ssa_bilag]
    ALLE_PUNKTER = STANDARD_PUNKTER + SSA_PUNKTER

    if not elementer:
        st.info("Ingen sjekkliste opprettet ennå.")
        if st.button("Opprett standardsjekkliste"):
            try:
                with httpx.Client(timeout=10) as client:
                    for tekst in ALLE_PUNKTER:
                        client.post(
                            f"{API_BASE}/sjekkliste",
                            json={
                                "varsling_id": varsling_id,
                                "profil_id": profil_id,
                                "tekst": tekst,
                                "ferdig": False,
                            },
                        )
                st.rerun()
            except Exception as e:
                st.error(f"Feil: {e}")
    else:
        ferdig_count = sum(1 for e in elementer if e.get("ferdig"))
        st.progress(ferdig_count / len(elementer), text=f"{ferdig_count}/{len(elementer)} fullført")

        for elem in elementer:
            col_check, col_tekst, col_frist = st.columns([1, 6, 2])
            with col_check:
                ny_status = st.checkbox(
                    "",
                    value=elem.get("ferdig", False),
                    key=f"chk_{elem['id']}",
                    label_visibility="collapsed",
                )
                if ny_status != elem.get("ferdig", False):
                    try:
                        with httpx.Client(timeout=10) as client:
                            client.put(
                                f"{API_BASE}/sjekkliste/{elem['id']}",
                                json={"ferdig": ny_status},
                            )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Feil: {e}")
            with col_tekst:
                tekst = elem.get("tekst", "")
                st.markdown(f"~~{tekst}~~" if elem.get("ferdig") else tekst)
            with col_frist:
                frist = elem.get("frist")
                if frist:
                    st.caption(f"Frist: {frist[:10]}")

    # Legg til nytt punkt
    st.divider()
    with st.expander("Legg til nytt sjekkpunkt"):
        ny_tekst = st.text_input("Beskrivelse")
        ny_frist = st.date_input("Frist (valgfritt)", value=None)
        if st.button("Legg til"):
            if ny_tekst:
                try:
                    with httpx.Client(timeout=10) as client:
                        client.post(
                            f"{API_BASE}/sjekkliste",
                            json={
                                "varsling_id": varsling_id,
                                "profil_id": profil_id,
                                "tekst": ny_tekst,
                                "ferdig": False,
                                "frist": str(ny_frist) if ny_frist else None,
                            },
                        )
                    st.rerun()
                except Exception as e:
                    st.error(f"Feil: {e}")

# ── Tab 2: ESPD-guide ────────────────────────────────────────────
with tab_espd:
    st.markdown("### ESPD — Europeisk egenerklæring (§17-1 FOA)")
    st.info(
        "ESPD (European Single Procurement Document) er en egenerklæring der leverandøren "
        "bekrefter at de oppfyller kvalifikasjonskravene. Fylles ut digitalt via "
        "[espd.dfo.no](https://espd.dfo.no) og legges ved tilbudet."
    )

    ESPD_DELER = [
        {
            "del": "Del I — Opplysninger om anskaffelsen",
            "beskrivelse": (
                "Informasjon om oppdragsgiveren og anskaffelsesprosedyren. "
                "Fylles normalt ut automatisk basert på kunngjøringen."
            ),
            "punkter": [
                "Oppdragsgiverens navn og adresse",
                "Anskaffelsens navn og referansenummer",
                "Prosedyretype (åpen, begrenset, osv.)",
            ],
        },
        {
            "del": "Del II — Opplysninger om leverandøren",
            "beskrivelse": "Grunnleggende identifikasjon av tilbyderen.",
            "punkter": [
                "Foretaksnavn og organisasjonsnummer",
                "Kontaktperson og adresse",
                "Om tilbudet leveres som del av et fellesforetak (konsortium)",
                "Eventuelle underleverandører (navn + andel av kontrakten)",
            ],
        },
        {
            "del": "Del III — Avvisningsgrunner (§24-2 FOA)",
            "beskrivelse": (
                "Egenerklæring om at foretaket ikke er ilagt straff for alvorlige lovbrudd "
                "(korrupsjon, hvitvasking, skatteunndragelse m.m.)."
            ),
            "punkter": [
                "Ingen dom for korrupsjon, terrorfinansiering eller hvitvasking",
                "Ingen alvorlig miljøkriminalitet eller brudd på arbeidsmiljølov",
                "Ikke i konkurs eller under avvikling",
                "Oppfylt plikt til å betale skatter og avgifter",
                "Egenerklæring russiske selskaper (FOA §24-2 — obligatorisk fra mars 2022)",
            ],
        },
        {
            "del": "Del IV — Kvalifikasjonskrav",
            "beskrivelse": (
                "Dokumentasjon av faglig og finansiell kapasitet. "
                "Svar 'Alle krav' med Ja, eller fyll ut hvert underpunkt."
            ),
            "punkter": [
                "α (alfa) — Generell erklæring: kryss Ja hvis dere oppfyller alle kvalifikasjonskrav",
                "A — Egnethet: registrert i foretaksregister, bransjeregister",
                "B — Finansiell kapasitet: omsetning, forsikring, regnskap",
                "C — Teknisk og faglig kapasitet: referanseprosjekter, nøkkelpersonell, utstyr",
            ],
        },
        {
            "del": "Del V — Begrensning av deltakelse i anskaffelsesprosessen",
            "beskrivelse": (
                "Erklæring om interessekonflikter og inhabilitet. "
                "Normalt ikke relevant for leverandører."
            ),
            "punkter": [
                "Ingen interessekonflikt med oppdragsgiveren",
                "Ikke involvert i forberedelsen av konkurransegrunnlaget",
            ],
        },
        {
            "del": "Del VI — Avsluttende erklæringer",
            "beskrivelse": (
                "Leverandøren bekrefter at alle opplysninger er korrekte og samtykker til "
                "at oppdragsgiver kan innhente dokumentasjon ved behov."
            ),
            "punkter": [
                "Bekreftelse på at alle opplysninger er korrekte",
                "Samtykke til at oppdragsgiver kan hente bekreftende dokumentasjon",
                "Dato og signatur (elektronisk via espd.dfo.no)",
            ],
        },
    ]

    for del_info in ESPD_DELER:
        with st.expander(del_info["del"]):
            st.caption(del_info["beskrivelse"])
            for punkt in del_info["punkter"]:
                st.markdown(f"- {punkt}")

    st.caption(
        "Kilde: DFØ ESPD-veileder og FOA §17-1. "
        "Systemet veileder — du er ansvarlig for innholdet."
    )

# ── Tab 3: SSA-bilag ─────────────────────────────────────────────
with tab_bilag:
    ssa_info = SSA_MAP.get(auto_ssa, {})
    st.markdown(f"### Avtaletype: {ssa_info.get('navn', auto_ssa)}")
    st.caption(
        f"Automatisk detektert fra CPV-koder og tittel. "
        f"Risikonivå: **{ssa_info.get('risiko_nivå', '?')}**"
    )
    st.caption(ssa_info.get("beskrivelse", ""))

    if ssa_bilag:
        st.markdown("**Kritiske bilag som MÅ fylles ut for denne avtaletypen:**")
        for b in ssa_bilag:
            st.markdown(f"- {b}")
    else:
        st.info("Ingen SSA-spesifikke bilag registrert for denne avtaletypen.")

    if ssa_info.get("risiko"):
        st.markdown("**Risikoadvarsler:**")
        for r in ssa_info["risiko"]:
            st.markdown(f"- {r}")

    st.divider()
    st.markdown("**Endre avtaletype:**")
    ssa_typer = list(SSA_MAP.keys())
    auto_idx = ssa_typer.index(auto_ssa) if auto_ssa in ssa_typer else 0
    manuell_ssa = st.selectbox(
        "SSA-type:",
        options=ssa_typer,
        index=auto_idx,
        format_func=lambda k: SSA_MAP[k]["navn"],
        key="manuell_ssa_tab",
    )
    if manuell_ssa != auto_ssa:
        annen = SSA_MAP[manuell_ssa]
        st.markdown(f"**{annen['navn']}** — {annen['beskrivelse']}")
        for b in annen["bilag"]:
            st.markdown(f"- {b}")
