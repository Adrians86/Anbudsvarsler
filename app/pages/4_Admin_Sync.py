"""Side 4 — Admin og synkronisering."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.theme import inject_css, section_header

st.set_page_config(page_title="Admin | Anbudsvarsler", page_icon="⚙️", layout="wide")
inject_css()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

section_header("⚙️ Admin og synkronisering")

st.markdown(
    "Her kan du manuelt synkronisere kunngjøringer fra Doffin og TED, "
    "og se status på databasen."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Manuell synkronisering")
    st.write("Henter kunngjøringer fra de siste 2 dagene.")
    if st.button("🔄 Synkroniser nå", type="primary"):
        with st.spinner("Synkroniserer..."):
            try:
                with httpx.Client(timeout=60) as client:
                    resp = client.post(f"{API_BASE}/admin/sync")
                    resp.raise_for_status()
                    data = resp.json()
                st.success("Synkronisering fullført!")
                st.metric("Nye kunngjøringer", data.get("nye_kunngjøringer", 0))
                st.metric("Nye varsler", data.get("nye_varsler", 0))
                st.metric("Totalt hentet", data.get("totalt_hentet", 0))
            except Exception as e:
                st.error(f"Synkroniseringsfeil: {e}")

with col2:
    st.subheader("Databasestatus")
    try:
        with httpx.Client(timeout=10) as client:
            health = client.get(f"{API_BASE}/health").json()
            kunngjøringer = client.get(f"{API_BASE}/kunngjoring").json()
        st.success(f"API status: {health.get('status', 'ukjent').upper()}")
        st.metric("Kunngjøringer i DB", len(kunngjøringer))
        st.write(f"API versjon: `{health.get('version', '?')}`")
    except Exception as e:
        st.error(f"API ikke tilgjengelig: {e}")
        st.info("Sørg for at API-serveren kjører: `uvicorn leverandor.api.main:app --reload`")

st.divider()
st.subheader("Konfigurering")
st.markdown(
    """
    **Miljøvariabler (.env):**
    - `DOFFIN_API_KEY` — API-nøkkel for Doffin Public API *(valgfri — faller tilbake til CSV)*
    - `DATABASE_URL` — Database URL *(standard: sqlite:///./anbudsvarsler.db)*
    - `ANTHROPIC_API_KEY` — For Phase 2 PDF-parsing

    **Registrer Doffin API-nøkkel:**
    Gå til https://dof-notices-prod-api.developer.azure-api.net/ og registrer deg gratis.
    """
)
