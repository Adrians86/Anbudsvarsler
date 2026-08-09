"""Side 3 — Søk etter kunngjøringer."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.theme import inject_css, section_header

st.set_page_config(page_title="Søk | Anbudsvarsler", page_icon="🔍", layout="wide")
inject_css()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

section_header("🔍 Søk etter kunngjøringer")

col1, col2, col3 = st.columns(3)
with col1:
    cpv_soek = st.text_input("CPV-kode", placeholder="72000000")
with col2:
    region_soek = st.text_input("NUTS-region", placeholder="NO011")
with col3:
    fra_dato = st.date_input("Publisert etter", value=None)

if st.button("Søk", type="primary"):
    params = {}
    if cpv_soek:
        params["cpv"] = cpv_soek
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
        st.error(f"Søkefeil: {e}")
        kunngjøringer = []

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
                if k.get("estimert_verdi"):
                    st.metric("Estimert verdi", f"{k['estimert_verdi']:,} NOK")
                if k.get("url"):
                    st.markdown(f"[Åpne kunngjøring]({k['url']})")
else:
    st.info("Skriv inn søkekriterier og trykk **Søk** for å finne kunngjøringer.")
    st.markdown(
        """
        **Tips:**
        - Søk på CPV-kode for å finne kunngjøringer innenfor din bransje
        - Bruk NUTS-region for å filtrere geografisk
        - Trykk **Søk** uten filtre for å se alle kunngjøringer i databasen
        """
    )
