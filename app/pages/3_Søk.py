"""Side 3 — Søk etter kunngjøringer."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.cpv_data import CPV_GRUPPER, NUTS_REGIONER, alle_oppslag
from app.theme import inject_css, section_header, status_pill

st.set_page_config(page_title="Søk | Anbudsvarsler", page_icon="🔍", layout="wide")
inject_css()

_ALLE_CPV = alle_oppslag()

section_header("🔍 Søk etter kunngjøringer", eyebrow="SØK I KUNNGJØRINGER")

# ── Reset-nøkkel for å tømme alle filterwidgets ──────────────────────────────
if "sok_reset_key" not in st.session_state:
    st.session_state["sok_reset_key"] = 0

reset_key = st.session_state["sok_reset_key"]

# ── Hent eksisterende varsler for aktiv profil (for status-pills) ─────────────
profil_id = st.session_state.get("profil_id")
_varsling_map: dict[int, dict] = {}  # {kunngjoring_id: varsling}
if profil_id:
    try:
        with httpx.Client(timeout=8) as client:
            v_resp = client.get(f"{API_BASE}/varsling", params={"profil_id": profil_id})
            if v_resp.status_code == 200:
                for _v in v_resp.json():
                    _varsling_map[_v["kunngjoring_id"]] = _v
    except Exception:
        pass

# ── CPV-gruppe filter ─────────────────────────────────────────────────────────
with st.expander("Filtrer på bransje / CPV-kode", expanded=True):
    cpv_valgt: list[str] = []
    cols = st.columns(2)
    bransjer = list(CPV_GRUPPER.items())
    for i, (bransje, koder) in enumerate(bransjer):
        with cols[i % 2]:
            valgte = st.multiselect(
                bransje,
                options=koder,
                key=f"sok_cpv_{bransje}_{reset_key}",
                placeholder="Velg...",
            )
            cpv_valgt.extend(valgte)

# ── Andre filtre ──────────────────────────────────────────────────────────────
col_nuts, col_dato = st.columns(2)
with col_nuts:
    region_display = st.selectbox(
        "NUTS-region",
        options=list(NUTS_REGIONER.keys()),
        index=0,
        key=f"nuts_{reset_key}",
        help="Velg geografisk region. 'Hele Norge' gir alle regioner.",
    )
    region_soek = NUTS_REGIONER[region_display]

with col_dato:
    fra_dato = st.date_input(
        "Publisert etter",
        value=None,
        key=f"fra_dato_{reset_key}",
    )

col_min_nok, col_max_nok = st.columns(2)
with col_min_nok:
    min_nok = st.number_input(
        "Min. estimert verdi (NOK)",
        min_value=0,
        value=0,
        step=100_000,
        key=f"min_nok_{reset_key}",
        help="0 = ingen nedre grense",
    )
with col_max_nok:
    max_nok = st.number_input(
        "Maks. estimert verdi (NOK)",
        min_value=0,
        value=0,
        step=500_000,
        key=f"max_nok_{reset_key}",
        help="0 = ingen øvre grense",
    )

# ── Knapper ───────────────────────────────────────────────────────────────────
col_sok, col_nullstill = st.columns([2, 1])
with col_sok:
    sok_klikket = st.button("Søk", type="primary", use_container_width=True)
with col_nullstill:
    if st.button("Nullstill filtre", use_container_width=True):
        st.session_state["sok_reset_key"] += 1
        # Fjern eventuelle cachet søkeresultater
        st.session_state.pop("_sok_resultater", None)
        st.rerun()

# ── Søk og vis resultater ────────────────────────────────────────────────────
if sok_klikket:
    valgte_koder = {_ALLE_CPV[k] for k in cpv_valgt if k in _ALLE_CPV}
    params: dict = {}
    if valgte_koder:
        params["cpv"] = next(iter(valgte_koder))
    if region_soek:
        params["region"] = region_soek
    if fra_dato:
        params["fra"] = str(fra_dato)

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{API_BASE}/kunngjoring", params=params)
            resp.raise_for_status()
            kunngjøringer = resp.json()
    except Exception as e:
        st.error(f"Søkefeil ({API_BASE}): {e}")
        kunngjøringer = []

    # Klient-side-filtrering for ytterligere CPV-koder
    if len(valgte_koder) > 1:
        kunngjøringer = [
            k for k in kunngjøringer
            if any(c in valgte_koder for c in k.get("cpv_koder", []))
        ]

    # Filtrer på estimert verdi
    if min_nok > 0:
        filtered = []
        for k in kunngjøringer:
            v = k.get("estimert_verdi")
            if v is not None:
                try:
                    if float(v) >= min_nok:
                        filtered.append(k)
                except (ValueError, TypeError):
                    pass
            # Kunngjøringer uten oppgitt verdi vises ikke når min_nok er satt
        kunngjøringer = filtered

    if max_nok > 0:
        filtered = []
        for k in kunngjøringer:
            v = k.get("estimert_verdi")
            if v is None:
                filtered.append(k)  # Ukjent verdi passerer øvre grense
            else:
                try:
                    if float(v) <= max_nok:
                        filtered.append(k)
                except (ValueError, TypeError):
                    filtered.append(k)
        kunngjøringer = filtered

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
                if k.get("nuts_region"):
                    st.write(f"**Region:** {k['nuts_region']}")
                if k.get("cpv_koder"):
                    st.write(f"**CPV:** {', '.join(k['cpv_koder'])}")
                if k.get("url"):
                    st.markdown(f"[Åpne kunngjøring]({k['url']})")
            with col2:
                verdi = k.get("estimert_verdi")
                if verdi is not None:
                    try:
                        st.metric("Estimert verdi", f"{float(verdi):,.0f} NOK".replace(",", " "))
                    except (ValueError, TypeError):
                        st.write(f"**Estimert verdi:** {verdi}")
                else:
                    st.write("**Estimert verdi:** Ikke oppgitt")

                # Vis status-pill om denne kunngjøringen allerede er i din varslingsliste
                kid = k.get("id")
                if kid and kid in _varsling_map:
                    vsl = _varsling_map[kid]
                    st.markdown(
                        status_pill(vsl["status"]), unsafe_allow_html=True
                    )
                    st.caption("Allerede i dine varsler")
else:
    st.info("Velg bransje og trykk **Søk** for å finne kunngjøringer.")
    st.markdown(
        """
        **Tips:**
        - Velg én eller flere bransjer fra nedtrekkslisten
        - Bruk NUTS-region for å filtrere geografisk
        - Bruk verdifiltrene for å begrense etter estimert kontraktsverdi
        - Trykk **Søk** uten filtre for å se alle kunngjøringer i databasen
        - Kunngjøringer som allerede er i din varslingsliste vises med status-pille
        """
    )
