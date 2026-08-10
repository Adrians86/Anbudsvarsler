"""Side 5 — Tilbudssjekkliste."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st
from datetime import datetime

from app.config import API_BASE_URL as API_BASE
from app.theme import inject_css, section_header

st.set_page_config(page_title="Tilbud | Anbudsvarsler", page_icon="📋", layout="wide")
inject_css()

section_header("📋 Tilbudssjekkliste")

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
    "Signere og sende inn tilbud innen fristen",
]

if not elementer:
    st.info("Ingen sjekkliste opprettet ennå.")
    if st.button("Opprett standardsjekkliste"):
        try:
            with httpx.Client(timeout=10) as client:
                for tekst in STANDARD_PUNKTER:
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
