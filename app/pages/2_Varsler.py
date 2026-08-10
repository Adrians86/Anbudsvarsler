"""Side 2 — Mine varsler."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.theme import inject_css, resultat_badge, section_header, status_pill

st.set_page_config(page_title="Varsler | Anbudsvarsler", page_icon="🔔", layout="wide")
inject_css()

section_header("🔔 Mine anbudsvarsler")

profil_id = st.session_state.get("profil_id")
if not profil_id:
    st.warning("Du må opprette en profil først. Gå til **Min Profil**.")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    status_filter = st.selectbox(
        "Filtrer på status",
        ["Alle", "NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"],
    )
with col2:
    min_score = st.slider("Minimum relevans-score", 0.0, 1.0, 0.0, 0.1)
with col3:
    if st.button("Oppdater liste"):
        st.rerun()

try:
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{API_BASE}/varsling", params={"profil_id": profil_id})
        resp.raise_for_status()
        varsler = resp.json()
except Exception as e:
    st.error(f"Klarte ikke hente varsler: {e}")
    st.stop()

if status_filter != "Alle":
    varsler = [v for v in varsler if v["status"] == status_filter]
varsler = [v for v in varsler if v["relevans_score"] >= min_score]

if not varsler:
    st.info("Ingen varsler funnet. Kjør en synkronisering fra Admin-siden.")
    st.stop()

st.write(f"Viser **{len(varsler)}** varsler")

for v in varsler:
    kunngjoring_id = v["kunngjoring_id"]
    try:
        with httpx.Client(timeout=10) as client:
            k_resp = client.get(f"{API_BASE}/kunngjoring/{kunngjoring_id}")
            k = k_resp.json() if k_resp.status_code == 200 else {}
    except Exception:
        k = {}

    with st.expander(
        f"📄 {k.get('tittel', 'Ukjent')} — Score: {v['relevans_score']:.2f}"
    ):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Oppdragsgiver:** {k.get('oppdragsgiver', 'Ukjent')}")
            if k.get("tilbudsfrist"):
                st.write(f"**Tilbudsfrist:** {k['tilbudsfrist'][:10]}")
            if k.get("estimert_verdi"):
                st.write(f"**Estimert verdi:** {k['estimert_verdi']:,} NOK")
            if k.get("cpv_koder"):
                st.write(f"**CPV-koder:** {', '.join(k['cpv_koder'])}")
            if k.get("url"):
                st.markdown(f"[Åpne på {k.get('kilde', 'Doffin')}]({k['url']})")

        with col2:
            st.markdown(status_pill(v["status"]), unsafe_allow_html=True)
            st.write(f"Relevans: **{v['relevans_score']:.0%}**")

            ny_status = st.selectbox(
                "Oppdater status",
                ["NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"],
                index=["NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"].index(
                    v["status"]
                ),
                key=f"status_{v['id']}",
            )
            if st.button("Lagre", key=f"save_{v['id']}"):
                try:
                    with httpx.Client(timeout=10) as client:
                        client.put(
                            f"{API_BASE}/varsling/{v['id']}/status",
                            params={"ny_status": ny_status},
                        )
                    st.toast("Status oppdatert!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Feil: {e}")

            if st.button("Sjekk kvalifikasjon", key=f"kval_{v['id']}"):
                try:
                    with httpx.Client(timeout=10) as client:
                        kval_resp = client.post(
                            f"{API_BASE}/kvalifikasjon",
                            json={"varsling_id": v["id"], "profil_id": profil_id},
                        )
                        kval = kval_resp.json()
                    st.markdown(
                        resultat_badge(kval["resultat"]), unsafe_allow_html=True
                    )
                    if kval["mangler"]:
                        st.warning("Mangler: " + ", ".join(kval["mangler"]))
                except Exception as e:
                    st.error(f"Feil: {e}")
