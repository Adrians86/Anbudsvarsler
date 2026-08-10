"""Side 7 — Fristmonitor dashboard."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st
from datetime import datetime, timedelta

from app.config import API_BASE_URL as API_BASE
from app.theme import inject_css, section_header

st.set_page_config(page_title="Frister | Anbudsvarsler", page_icon="⏰", layout="wide")
inject_css()

section_header("⏰ Fristmonitor")

profil_id = st.session_state.get("profil_id")
if not profil_id:
    st.warning("Du må fylle inn din leverandørprofil på siden **Min profil** først.")
    st.stop()

# Hent varslinger
try:
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{API_BASE}/varsling", params={"profil_id": profil_id})
        resp.raise_for_status()
        varslinger = resp.json()
except Exception as e:
    st.error(f"Kunne ikke hente varslinger: {e}")
    varslinger = []

nå = datetime.utcnow()


def _trafikklys(frist_str: str | None) -> tuple[str, str]:
    """Returner (farge_emoji, dager_tekst) basert på dager til frist."""
    if not frist_str:
        return "⚪", "Ingen frist"
    try:
        frist = datetime.fromisoformat(frist_str[:19])
    except ValueError:
        return "⚪", "Ukjent frist"
    dager = (frist - nå).days
    if dager < 0:
        return "⚫", f"Utgått ({abs(dager)}d siden)"
    if dager <= 7:
        return "🔴", f"{dager} dager igjen"
    if dager <= 21:
        return "🟡", f"{dager} dager igjen"
    return "🟢", f"{dager} dager igjen"


# Statistikk-rad
med_frist = [v for v in varslinger if v.get("tilbudsfrist")]
snart = [v for v in med_frist if _trafikklys(v["tilbudsfrist"])[0] in ("🔴", "🟡")]

col1, col2, col3 = st.columns(3)
col1.metric("Totalt aktive", len(varslinger))
col2.metric("Med tilbudsfrist", len(med_frist))
col3.metric("Frister innen 3 uker", len(snart))

st.divider()

# Sorter etter frist (nærmeste først, deretter uten frist)
def _sort_key(v):
    frist = v.get("tilbudsfrist")
    if not frist:
        return datetime(9999, 12, 31)
    try:
        return datetime.fromisoformat(frist[:19])
    except ValueError:
        return datetime(9999, 12, 31)

sorterte = sorted(varslinger, key=_sort_key)

# Filtrer status
status_filter = st.multiselect(
    "Filtrer på status",
    options=["NY", "SETT", "INTERESSERT", "FORKASTET"],
    default=["NY", "SETT", "INTERESSERT"],
)
if status_filter:
    sorterte = [v for v in sorterte if v.get("status", "NY") in status_filter]

if not sorterte:
    st.info("Ingen varslinger å vise med valgte filtre.")
else:
    for v in sorterte:
        lys, dager_tekst = _trafikklys(v.get("tilbudsfrist"))
        tittel = v.get("tittel", "Ukjent tittel")
        oppdragsgiver = v.get("oppdragsgiver", "")
        status = v.get("status", "NY")
        score = v.get("relevans_score", 0)

        with st.container(border=True):
            col_lys, col_info, col_meta = st.columns([1, 6, 2])
            with col_lys:
                st.markdown(f"# {lys}")
                st.caption(dager_tekst)
            with col_info:
                st.markdown(f"**{tittel}**")
                st.caption(f"{oppdragsgiver}")
                if v.get("cpv_koder"):
                    st.caption(f"CPV: {', '.join(v['cpv_koder'][:3])}")
            with col_meta:
                st.markdown(f"**Score:** {score:.0%}")
                st.markdown(f"**Status:** {status}")
                verdi = v.get("estimert_verdi")
                if verdi:
                    try:
                        st.caption(f"{float(verdi):,.0f} NOK".replace(",", " "))
                    except (ValueError, TypeError):
                        pass
                if v.get("url"):
                    st.markdown(f"[Åpne]({v['url']})")

                ny_status = st.selectbox(
                    "Oppdater status",
                    options=["NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"],
                    index=["NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"].index(status),
                    key=f"status_{v['id']}",
                    label_visibility="collapsed",
                )
                if ny_status != status:
                    try:
                        with httpx.Client(timeout=10) as client:
                            client.put(
                                f"{API_BASE}/varsling/{v['id']}",
                                json={"status": ny_status},
                            )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Feil: {e}")
