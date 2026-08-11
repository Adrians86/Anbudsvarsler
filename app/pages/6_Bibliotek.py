"""Side 6 — Innholdsbibliotek (dokumenter, maler, referanser)."""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.cpv_data import DOKUMENT_KATEGORIER
from app.theme import inject_css, section_header

st.set_page_config(page_title="Bibliotek | Anbudsvarsler", page_icon="📚", layout="wide")
inject_css()

section_header("📚 Innholdsbibliotek", eyebrow="INNHOLDSBIBLIOTEK")

profil_id = st.session_state.get("profil_id")
if not profil_id:
    st.warning("Du må fylle inn din leverandørprofil på siden **Min profil** først.")
    st.stop()

# ── Hjelpefunksjoner ─────────────────────────────────────────────────────────


def _utloep_ikon(dok: dict) -> str:
    """Returner statusikon for dokumentets utløpsdato."""
    if not dok.get("lastet_opp"):
        return "⬜"
    utloep = dok.get("utloep_dato")
    if not utloep:
        return "✅"
    try:
        utloep_dt = datetime.fromisoformat(utloep[:19])
    except ValueError:
        return "✅"
    nå = datetime.utcnow()
    dager = (utloep_dt - nå).days
    if dager < 0:
        return "🔴"
    if dager <= 30:
        return "🟡"
    return "✅"


def _format_nok(verdi) -> str:
    if verdi is None:
        return "—"
    try:
        return f"{int(verdi):,} NOK".replace(",", " ")
    except (ValueError, TypeError):
        return str(verdi)


# ── Hent data ────────────────────────────────────────────────────────────────

try:
    with httpx.Client(timeout=10) as client:
        dok_resp = client.get(f"{API_BASE}/dokument/{profil_id}")
        dok_resp.raise_for_status()
        dokumenter = dok_resp.json()
except Exception as e:
    st.error(f"Kunne ikke hente dokumenter: {e}")
    dokumenter = []

try:
    with httpx.Client(timeout=10) as client:
        mal_resp = client.get(f"{API_BASE}/bibliotek/{profil_id}", params={"kategori": "mal"})
        mal_resp.raise_for_status()
        maler = mal_resp.json()
except Exception as e:
    st.error(f"Kunne ikke hente maler: {e}")
    maler = []

try:
    with httpx.Client(timeout=10) as client:
        ref_resp = client.get(f"{API_BASE}/referanse/{profil_id}")
        ref_resp.raise_for_status()
        referanser = ref_resp.json()
except Exception as e:
    st.error(f"Kunne ikke hente referanser: {e}")
    referanser = []

# ── Metrics-rad ──────────────────────────────────────────────────────────────

total_dok = len(dokumenter)
lastet_opp = sum(1 for d in dokumenter if d.get("lastet_opp"))
utloper_snart = sum(
    1 for d in dokumenter
    if d.get("lastet_opp") and _utloep_ikon(d) == "🟡"
)

col1, col2, col3 = st.columns(3)
col1.metric("Totalt dokumenter", total_dok)
col2.metric("Lastet opp", lastet_opp)
col3.metric("Utløper innen 30 dager", utloper_snart)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_dok, tab_mal, tab_ref = st.tabs(["📄 Dokumenter", "📝 Maler", "🏆 Referanser"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — DOKUMENTER
# ════════════════════════════════════════════════════════════════════════════
with tab_dok:
    col_info, col_btn = st.columns([5, 1])
    with col_info:
        st.markdown(
            "Compliance-dokumenter som kreves ved offentlige anskaffelser (FOA kap. 16 / §24-2)."
        )
    with col_btn:
        vis_skjema = st.toggle("Legg til dokument", key="vis_dok_skjema")

    if vis_skjema:
        with st.form("nytt_dokument"):
            st.markdown("**Nytt firmadokument**")
            kat_visning = {v: k for k, v in DOKUMENT_KATEGORIER.items()}
            kat_valgt_vis = st.selectbox(
                "Kategori",
                options=list(DOKUMENT_KATEGORIER.values()),
            )
            kat_valgt = kat_visning[kat_valgt_vis]
            tittel = st.text_input("Tittel *", placeholder="f.eks. Skatteattest 2025")
            utloep = st.date_input("Utløpsdato (valgfri)", value=None)
            lastet = st.checkbox("Allerede lastet opp / tilgjengelig")

            if st.form_submit_button("Lagre dokument", type="primary"):
                if not tittel:
                    st.error("Tittel er obligatorisk.")
                else:
                    payload: dict = {
                        "profil_id": profil_id,
                        "kategori": kat_valgt,
                        "tittel": tittel,
                        "lastet_opp": lastet,
                    }
                    if utloep:
                        payload["utloep_dato"] = utloep.isoformat() + "T00:00:00"
                    try:
                        with httpx.Client(timeout=10) as client:
                            r = client.post(f"{API_BASE}/dokument", json=payload)
                            r.raise_for_status()
                        st.toast("Dokument lagret!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Feil ved lagring: {e}")

    # ── Vis dokumenter gruppert per DOKUMENT_KATEGORIER ──────────────────
    # Bygg et oppslag kategori → [dok]
    dok_per_kat: dict[str, list] = {k: [] for k in DOKUMENT_KATEGORIER}
    for d in dokumenter:
        kat = d.get("kategori", "annet")
        if kat not in dok_per_kat:
            kat = "annet"
        dok_per_kat[kat].append(d)

    for kat_key, kat_label in DOKUMENT_KATEGORIER.items():
        doks = dok_per_kat.get(kat_key, [])
        # Vis alltid alle kategorier (med placeholder om mangler)
        if doks:
            st.markdown(f"##### {kat_label}")
            for d in doks:
                ikon = _utloep_ikon(d)
                tittel_dok = d.get("tittel", kat_label)
                utloep_str = ""
                if d.get("utloep_dato"):
                    utloep_str = f" · utløper {d['utloep_dato'][:10]}"
                with st.expander(f"{ikon} {tittel_dok}{utloep_str}"):
                    col_meta, col_slett = st.columns([5, 1])
                    with col_meta:
                        st.caption(f"Kategori: {kat_label}")
                        if d.get("lastet_opp"):
                            st.success("Lastet opp", icon="✅")
                        else:
                            st.warning("Ikke lastet opp ennå", icon="⬜")
                        if d.get("utloep_dato"):
                            st.caption(f"Utløpsdato: {d['utloep_dato'][:10]}")
                    with col_slett:
                        if st.button("Slett", key=f"slett_dok_{d['id']}"):
                            try:
                                with httpx.Client(timeout=10) as client:
                                    client.delete(f"{API_BASE}/dokument/{d['id']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Feil: {e}")
        else:
            # Vis kategorien som tom (ikke lastet opp)
            st.markdown(f"##### ⬜ {kat_label}")
            st.caption("Ikke registrert — klikk 'Legg til dokument' for å registrere.")

    st.divider()
    st.caption(
        "Ikonforklaring: ✅ gyldig · 🟡 utløper innen 30 dager · 🔴 utgått · ⬜ ikke lastet opp"
    )

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — MALER
# ════════════════════════════════════════════════════════════════════════════
with tab_mal:
    col_mal_info, col_ny_mal = st.columns([5, 1])
    with col_mal_info:
        st.markdown("Maler for tilbudsbrev, CVer, metodebeskrivelser m.m.")
    with col_ny_mal:
        vis_mal_skjema = st.toggle("Ny mal", key="vis_mal_skjema")

    if vis_mal_skjema:
        with st.form("ny_mal"):
            st.markdown("**Nytt malelement**")
            mal_tittel = st.text_input("Tittel *")
            mal_innhold = st.text_area("Innhold / beskrivelse", height=180)
            mal_tags_input = st.text_input(
                "Tags (komma-separert)", placeholder="ISO 9001, bygg, offentlig"
            )
            if st.form_submit_button("Lagre mal", type="primary"):
                if not mal_tittel:
                    st.error("Tittel er obligatorisk.")
                else:
                    tags = [t.strip() for t in mal_tags_input.split(",") if t.strip()]
                    try:
                        with httpx.Client(timeout=10) as client:
                            r = client.post(
                                f"{API_BASE}/bibliotek",
                                json={
                                    "profil_id": profil_id,
                                    "kategori": "mal",
                                    "tittel": mal_tittel,
                                    "innhold": mal_innhold,
                                    "tags": tags,
                                },
                            )
                            r.raise_for_status()
                        st.toast("Mal lagret!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Feil: {e}")

    if not maler:
        st.info("Ingen maler ennå. Legg til tilbudsmaler, CVer og metodebeskrivelser.")
    else:
        st.markdown(f"**{len(maler)} maler**")
        for mal in maler:
            tags = mal.get("tags", [])
            tag_str = "  ".join(f"`{t}`" for t in tags) if tags else ""
            with st.expander(f"📝 {mal.get('tittel', 'Ukjent')}"):
                if mal.get("innhold"):
                    st.markdown(mal["innhold"])
                if tag_str:
                    st.markdown(tag_str)
                col_dato, col_slett = st.columns([4, 1])
                with col_dato:
                    dato = mal.get("created_at", "")
                    if dato:
                        st.caption(f"Lagt til: {dato[:10]}")
                with col_slett:
                    if st.button("Slett", key=f"slett_mal_{mal['id']}"):
                        try:
                            with httpx.Client(timeout=10) as client:
                                client.delete(f"{API_BASE}/bibliotek/{mal['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Feil: {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — REFERANSER
# ════════════════════════════════════════════════════════════════════════════
with tab_ref:
    col_ref_info, col_ny_ref = st.columns([5, 1])
    with col_ref_info:
        st.markdown("Tidligere oppdrag som dokumenterer faglig erfaring (FOA §16-8).")
    with col_ny_ref:
        vis_ref_skjema = st.toggle("Ny referanse", key="vis_ref_skjema")

    if vis_ref_skjema:
        with st.form("ny_referanse"):
            st.markdown("**Nytt referanseprosjekt**")
            ref_navn = st.text_input("Prosjektnavn *")
            ref_oppdrag = st.text_input("Oppdragsgiver *")
            ref_fra = st.text_input("Periode fra (ÅÅÅÅ-MM)", placeholder="2023-01")
            ref_til = st.text_input("Periode til (ÅÅÅÅ-MM)", placeholder="2024-06")
            ref_verdi = st.number_input("Kontraktsverdi (NOK)", min_value=0, step=100000, value=0)
            ref_cpv = st.text_input("CPV-kode", placeholder="72000000")
            ref_besk = st.text_area("Beskrivelse", height=120)
            ref_kontakt = st.text_input("Kontaktperson")
            ref_kan_kontaktes = st.checkbox("Kan kontaktes", value=True)
            if st.form_submit_button("Lagre referanse", type="primary"):
                if not ref_navn or not ref_oppdrag:
                    st.error("Prosjektnavn og oppdragsgiver er obligatorisk.")
                else:
                    payload = {
                        "profil_id": profil_id,
                        "prosjektnavn": ref_navn,
                        "oppdragsgiver_navn": ref_oppdrag,
                        "periode_fra": ref_fra or None,
                        "periode_til": ref_til or None,
                        "kontraktsverdi_nok": int(ref_verdi) if ref_verdi else None,
                        "cpv": ref_cpv or None,
                        "beskrivelse": ref_besk or None,
                        "kontaktperson": ref_kontakt or None,
                        "kan_kontaktes": ref_kan_kontaktes,
                    }
                    try:
                        with httpx.Client(timeout=10) as client:
                            r = client.post(f"{API_BASE}/referanse", json=payload)
                            r.raise_for_status()
                        st.toast("Referanse lagret!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Feil: {e}")

    if not referanser:
        st.info(
            "Ingen referanseprosjekter ennå. "
            "Legg til tidligere oppdrag for å dokumentere faglig erfaring."
        )
    else:
        st.markdown(f"**{len(referanser)} referanseprosjekter**")
        for ref in referanser:
            periode = ""
            if ref.get("periode_fra") or ref.get("periode_til"):
                periode = f"{ref.get('periode_fra', '?')} – {ref.get('periode_til', 'pågående')}"
            kan_kontaktes_str = "✅ Kan kontaktes" if ref.get("kan_kontaktes") else "🚫 Kan ikke kontaktes"
            header = f"🏆 {ref.get('prosjektnavn', 'Ukjent')} — {ref.get('oppdragsgiver_navn', '')}"
            with st.expander(header):
                col_a, col_b = st.columns([3, 2])
                with col_a:
                    if periode:
                        st.caption(f"Periode: {periode}")
                    if ref.get("kontraktsverdi_nok"):
                        st.caption(f"Kontraktsverdi: {_format_nok(ref['kontraktsverdi_nok'])}")
                    if ref.get("cpv"):
                        st.caption(f"CPV: {ref['cpv']}")
                    if ref.get("beskrivelse"):
                        st.markdown(ref["beskrivelse"])
                with col_b:
                    st.markdown(kan_kontaktes_str)
                    if ref.get("kontaktperson"):
                        st.caption(f"Kontakt: {ref['kontaktperson']}")
                    if st.button("Slett", key=f"slett_ref_{ref['id']}"):
                        try:
                            with httpx.Client(timeout=10) as client:
                                client.delete(f"{API_BASE}/referanse/{ref['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Feil: {e}")
