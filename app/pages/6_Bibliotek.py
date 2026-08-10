"""Side 6 — Innholdsbibliotek."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.theme import inject_css, section_header

st.set_page_config(page_title="Bibliotek | Anbudsvarsler", page_icon="📚", layout="wide")
inject_css()

section_header("📚 Innholdsbibliotek", eyebrow="INNHOLDSBIBLIOTEK")

profil_id = st.session_state.get("profil_id")
if not profil_id:
    st.warning("Du må fylle inn din leverandørprofil på siden **Min profil** først.")
    st.stop()

KATEGORIER = ["sertifikat", "årsregnskap", "referanse", "mal", "annet"]

col_filter, col_ny = st.columns([3, 1])
with col_filter:
    valgt_kat = st.selectbox("Filtrer kategori", options=["Alle"] + KATEGORIER)
with col_ny:
    st.markdown("&nbsp;", unsafe_allow_html=True)
    vis_skjema = st.toggle("Legg til dokument")

if vis_skjema:
    with st.form("nytt_element"):
        st.markdown("**Nytt bibliotekelement**")
        tittel = st.text_input("Tittel *")
        kategori = st.selectbox("Kategori", options=KATEGORIER)
        innhold = st.text_area("Innhold / beskrivelse", height=150)
        tags_input = st.text_input("Tags (komma-separert)", placeholder="ISO 9001, bygg, offentlig")
        if st.form_submit_button("Lagre", type="primary"):
            if not tittel:
                st.error("Tittel er obligatorisk.")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                try:
                    with httpx.Client(timeout=10) as client:
                        resp = client.post(
                            f"{API_BASE}/bibliotek",
                            json={
                                "profil_id": profil_id,
                                "kategori": kategori,
                                "tittel": tittel,
                                "innhold": innhold,
                                "tags": tags,
                            },
                        )
                        resp.raise_for_status()
                    st.toast("Lagret!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Feil: {e}")

# Hent og vis biblioteket
try:
    params = {"profil_id": profil_id}
    if valgt_kat != "Alle":
        params["kategori"] = valgt_kat
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{API_BASE}/bibliotek/{profil_id}", params=params)
        resp.raise_for_status()
        elementer = resp.json()
except Exception as e:
    st.error(f"Kunne ikke hente bibliotek: {e}")
    elementer = []

if not elementer:
    st.info("Biblioteket er tomt. Legg til sertifikater, referanser og maler.")
else:
    st.markdown(f"**{len(elementer)} elementer**")

    kat_rekkefølge = KATEGORIER if valgt_kat == "Alle" else [valgt_kat]
    for kat in kat_rekkefølge:
        i_kat = [e for e in elementer if e.get("kategori") == kat]
        if not i_kat:
            continue
        st.markdown(f"### {kat.capitalize()}")
        for elem in i_kat:
            with st.expander(elem.get("tittel", "Ukjent")):
                if elem.get("innhold"):
                    st.markdown(elem["innhold"])
                tags = elem.get("tags", [])
                if tags:
                    st.caption("Tags: " + " · ".join(tags))
                col_dato, col_slett = st.columns([4, 1])
                with col_dato:
                    dato = elem.get("created_at", "")
                    if dato:
                        st.caption(f"Lagt til: {dato[:10]}")
                with col_slett:
                    if st.button("Slett", key=f"slett_{elem['id']}"):
                        try:
                            with httpx.Client(timeout=10) as client:
                                client.delete(f"{API_BASE}/bibliotek/{elem['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Feil: {e}")
