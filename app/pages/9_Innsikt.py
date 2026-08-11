"""Side 9 — Innsikt og statistikk."""
import os
import sys
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st
import pandas as pd

from app.config import API_BASE_URL as API_BASE
from app.theme import inject_css, section_header

st.set_page_config(page_title="Innsikt | Anbudsvarsler", page_icon="📊", layout="wide")
inject_css()

section_header("📊 Innsikt og statistikk", eyebrow="INNSIKT")

profil_id = st.session_state.get("profil_id")

# ── Hent data ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def hent_kunngjøringer() -> list:
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE}/kunngjoring")
            r.raise_for_status()
            return r.json()
    except Exception:
        return []


@st.cache_data(ttl=60)
def hent_varslinger(pid: int) -> list:
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE}/varsling", params={"profil_id": pid})
            r.raise_for_status()
            return r.json()
    except Exception:
        return []


@st.cache_data(ttl=60)
def hent_kvalifikasjoner(pid: int) -> list:
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{API_BASE}/kvalifikasjon", params={"profil_id": pid})
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return []


kunngjøringer = hent_kunngjøringer()
varslinger = hent_varslinger(profil_id) if profil_id else []
kvalifikasjoner = hent_kvalifikasjoner(profil_id) if profil_id else []

# ── Metrics-rad ──────────────────────────────────────────────────────────────

total_kunngjøringer = len(kunngjøringer)
aktive_varsler = len(varslinger)

if varslinger:
    snitt_score = sum(v.get("relevans_score", 0) for v in varslinger) / len(varslinger)
    snitt_str = f"{snitt_score:.0%}"
else:
    snitt_str = "—"

if kvalifikasjoner:
    resultat_teller = Counter(k.get("resultat", "") for k in kvalifikasjoner)
    go_count = resultat_teller.get("GO", 0)
    ga_videre_count = resultat_teller.get("GÅ VIDERE MED FORBEHOLD", 0)
    no_go_count = resultat_teller.get("NO-GO", 0)
    kvali_str = f"GO:{go_count} / GV:{ga_videre_count} / NO-GO:{no_go_count}"
else:
    kvali_str = "—"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Kunngjøringer i DB", total_kunngjøringer)
col2.metric("Aktive varsler", aktive_varsler if profil_id else "—")
col3.metric("Gj.snitt relevans-score", snitt_str if profil_id else "—")
col4.metric("GO / GV / NO-GO", kvali_str if profil_id else "—")

if not profil_id:
    st.info(
        "For profilspesifikk statistikk, gå til **Min profil** og velg din leverandørprofil."
    )

st.divider()

# ── Status-fordeling ─────────────────────────────────────────────────────────

ALLE_STATUSER = ["NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"]

if varslinger:
    st.markdown("### Status-fordeling")
    status_teller = Counter(v.get("status", "NY") for v in varslinger)
    status_df = pd.DataFrame(
        {"Antall": [status_teller.get(s, 0) for s in ALLE_STATUSER]},
        index=ALLE_STATUSER,
    )
    st.bar_chart(status_df)
elif profil_id:
    st.markdown("### Status-fordeling")
    st.info("Ingen varslinger å vise ennå.")

# ── Relevans-fordeling ───────────────────────────────────────────────────────

if varslinger:
    st.markdown("### Relevans-fordeling")
    buckets = {"0–25 %": 0, "25–50 %": 0, "50–75 %": 0, "75–100 %": 0}
    for v in varslinger:
        score = v.get("relevans_score", 0)
        if score < 0.25:
            buckets["0–25 %"] += 1
        elif score < 0.50:
            buckets["25–50 %"] += 1
        elif score < 0.75:
            buckets["50–75 %"] += 1
        else:
            buckets["75–100 %"] += 1
    rel_df = pd.DataFrame(
        {"Antall": list(buckets.values())},
        index=list(buckets.keys()),
    )
    st.bar_chart(rel_df)

# ── Frister denne måneden ────────────────────────────────────────────────────

if varslinger:
    st.markdown("### Frister de neste 30 dagene")
    nå = datetime.utcnow()
    grense = nå + timedelta(days=30)

    def _dager_til(frist_str: str | None) -> int | None:
        if not frist_str:
            return None
        try:
            frist = datetime.fromisoformat(frist_str[:19])
            return (frist - nå).days
        except ValueError:
            return None

    kommende = [
        v for v in varslinger
        if v.get("tilbudsfrist") and _dager_til(v["tilbudsfrist"]) is not None
        and 0 <= (_dager_til(v["tilbudsfrist"]) or 9999) <= 30
    ]
    kommende_sortert = sorted(kommende, key=lambda v: v.get("tilbudsfrist", ""))

    if not kommende_sortert:
        st.info("Ingen tilbudsfrister de neste 30 dagene.")
    else:
        for v in kommende_sortert:
            dager = _dager_til(v.get("tilbudsfrist")) or 0
            if dager <= 7:
                lys = "🔴"
            elif dager <= 21:
                lys = "🟡"
            else:
                lys = "🟢"
            tittel = v.get("tittel", "Ukjent")
            frist_str = (v.get("tilbudsfrist") or "")[:10]
            st.markdown(
                f"{lys} **{tittel}** — frist {frist_str} ({dager} dager igjen)"
            )

# ── Kunngjøringer per kilde ──────────────────────────────────────────────────

st.markdown("### Kunngjøringer per kilde")

if kunngjøringer:
    kilde_teller = Counter(k.get("kilde", "UKJENT") for k in kunngjøringer)
    kilde_df = pd.DataFrame(
        {"Antall": list(kilde_teller.values())},
        index=list(kilde_teller.keys()),
    )
    st.bar_chart(kilde_df)
else:
    st.info("Ingen kunngjøringer i databasen ennå.")
