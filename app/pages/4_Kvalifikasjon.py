"""Side 4 — GO / NO-GO kvalifikasjonssjekk."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.theme import inject_css, section_header

st.set_page_config(page_title="Kvalifikasjon | Anbudsvarsler", page_icon="✅", layout="wide")
inject_css()

section_header("✅ GO / NO-GO kvalifikasjonssjekk")

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
    st.info("Ingen varslinger funnet. Prøv å synkronisere data via Admin-siden.")
    st.stop()

varsling_valg = {
    f"{v.get('id')} — {v.get('tittel', 'Ukjent')} (score: {v.get('relevans_score', 0):.0%})": v
    for v in varslinger
}

valgt_label = st.selectbox("Velg kunngjøring å vurdere:", options=list(varsling_valg.keys()))
valgt = varsling_valg[valgt_label]
varsling_id = valgt["id"]

col_info, col_sjekk = st.columns([2, 1])

with col_info:
    st.markdown(f"**Tittel:** {valgt.get('tittel', '')}")
    st.markdown(f"**Oppdragsgiver:** {valgt.get('oppdragsgiver', '')}")
    if valgt.get("tilbudsfrist"):
        st.markdown(f"**Tilbudsfrist:** {valgt['tilbudsfrist'][:10]}")
    if valgt.get("cpv_koder"):
        st.markdown(f"**CPV:** {', '.join(valgt['cpv_koder'])}")
    verdi = valgt.get("estimert_verdi")
    if verdi:
        try:
            st.markdown(f"**Estimert verdi:** {float(verdi):,.0f} NOK".replace(",", " "))
        except (ValueError, TypeError):
            pass

with col_sjekk:
    if st.button("Kjør GO / NO-GO sjekk", type="primary"):
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{API_BASE}/kvalifikasjon",
                    json={"varsling_id": varsling_id, "profil_id": profil_id},
                )
                resp.raise_for_status()
                sjekk = resp.json()
            st.session_state["siste_sjekk"] = sjekk
        except Exception as e:
            st.error(f"Feil under kvalifikasjonssjekk: {e}")

sjekk = st.session_state.get("siste_sjekk")
if sjekk:
    resultat = sjekk.get("resultat", "")
    st.divider()

    if resultat == "GO":
        st.success(f"## GO — Dere er kvalifisert!")
    elif resultat == "NO-GO":
        st.error(f"## NO-GO — Dere møter ikke kravene")
    else:
        st.warning(f"## GÅ VIDERE MED FORBEHOLD")

    mangler = sjekk.get("mangler", [])
    diskval = sjekk.get("diskvalifiserende", [])

    if diskval:
        st.markdown("**Diskvalifiserende mangler:**")
        for m in diskval:
            st.markdown(f"- ❌ {m}")

    if mangler:
        st.markdown("**Andre mangler / forbehold:**")
        for m in mangler:
            st.markdown(f"- ⚠️ {m}")

    rule_hits = sjekk.get("rule_hits", [])
    if rule_hits:
        with st.expander("Regelgrunnlag (FOA-referanser)"):
            for hit in rule_hits:
                st.markdown(f"- **{hit.get('regel', '')}**: {hit.get('beskrivelse', '')}")

    st.caption("Systemet anbefaler — du bestemmer. Bekreft vurderingen under.")
    if st.button("Bekreft vurdering og gå videre"):
        try:
            with httpx.Client(timeout=10) as client:
                client.put(
                    f"{API_BASE}/kvalifikasjon/{sjekk['id']}",
                    json={"bekreftet_av_bruker": True},
                )
            st.toast("Vurdering bekreftet!", icon="✅")
        except Exception as e:
            st.error(f"Feil: {e}")
