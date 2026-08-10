"""Side 3 — Søk etter kunngjøringer."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.cpv_data import CPV_GRUPPER, alle_oppslag
from app.theme import inject_css, section_header

st.set_page_config(page_title="Søk | Anbudsvarsler", page_icon="🔍", layout="wide")
inject_css()

_ALLE_CPV = alle_oppslag()

section_header("🔍 Søk etter kunngjøringer")

with st.expander("Filtrer på bransje / CPV-kode", expanded=True):
    cpv_valgt: list[str] = []
    cols = st.columns(2)
    bransjer = list(CPV_GRUPPER.items())
    for i, (bransje, koder) in enumerate(bransjer):
        with cols[i % 2]:
            valgte = st.multiselect(
                bransje,
                options=koder,
                key=f"sok_cpv_{bransje}",
                placeholder="Velg...",
            )
            cpv_valgt.extend(valgte)

col2, col3 = st.columns(2)
with col2:
    region_soek = st.text_input("NUTS-region", placeholder="NO011")
with col3:
    fra_dato = st.date_input("Publisert etter", value=None)

if st.button("Søk", type="primary"):
    valgte_koder = {_ALLE_CPV[k] for k in cpv_valgt if k in _ALLE_CPV}
    params = {}
    if valgte_koder:
        params["cpv"] = next(iter(valgte_koder))
    if region_soek:
        params["region"] = region_soek
    if fra_dato:
        params["fra"] = str(fra_dato)

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{API_BASE}/kunngjoring", params=params)
            resp.raise_for_status()
            kunngjøringer = resp.json()
    except Exception as e:
        st.error(f"Søkefeil ({API_BASE}): {e}")
        kunngjøringer = []

    if len(valgte_koder) > 1:
        kunngjøringer = [
            k for k in kunngjøringer
            if any(c in valgte_koder for c in k.get("cpv_koder", []))
        ]

    st.write(f"Fant **{len(kunngjøringer)}** kunngjøringer")

    for k in kunngjøringer:
        with st.expander(f"📄 {k.get('tittel', 'Ukjent tittel')}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Oppdragsgiver:** {k.get('oppdragsgiver', '')}")
                st.write(f"**Kilde:** {k.get('kilde', '')}")
                if k.get("publisert"):
                    st.write(f"**Publisert:** {k['publisert'][:10]}")
                if k.get("tilbudsfrist"):
                    st.write(f"**Frist:** {k['tilbudsfrist'][:10]}")
                if k.get("cpv_koder"):
                    st.write(f"**CPV:** {', '.join(k['cpv_koder'])}")
            with col2:
                verdi = k.get("estimert_verdi")
                if verdi:
                    try:
                        st.metric("Estimert verdi", f"{float(verdi):,.0f} NOK".replace(",", " "))
                    except (ValueError, TypeError):
                        st.write(f"**Estimert verdi:** {verdi}")
                else:
                    st.write("**Estimert verdi:** Ikke oppgitt")
                if k.get("url"):
                    st.markdown(f"[Åpne kunngjøring]({k['url']})")
else:
    st.info("Velg bransje og trykk **Søk** for å finne kunngjøringer.")
    st.markdown(
        """
        **Tips:**
        - Velg én eller flere bransjer fra nedtrekkslisten
        - Bruk NUTS-region for å filtrere geografisk (f.eks. `NO011` for Oslo)
        - Trykk **Søk** uten filtre for å se alle kunngjøringer i databasen
        """
    )
