"""Side 1 — Min profil."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
import streamlit as st

from app.theme import inject_css, section_header

st.set_page_config(page_title="Min profil | Anbudsvarsler", page_icon="🏢", layout="wide")
inject_css()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

VANLIGE_CPV = {
    "72000000 — IT-tjenester": "72000000",
    "45000000 — Bygge- og anleggsarbeid": "45000000",
    "71000000 — Arkitekt-, ingeniør- og planleggingstjenester": "71000000",
    "80000000 — Undervisnings- og opplæringstjenester": "80000000",
    "85000000 — Helse og sosiale tjenester": "85000000",
    "90000000 — Kloakk-, avfalls-, renholds- og miljøtjenester": "90000000",
    "79000000 — Forretningstjenester": "79000000",
    "60000000 — Transport": "60000000",
}

NUTS_REGIONER = {
    "Hele Norge": "",
    "Oslo (NO011)": "NO011",
    "Akershus (NO012)": "NO012",
    "Innlandet (NO020)": "NO020",
    "Viken (NO030)": "NO030",
    "Vestfold og Telemark (NO040)": "NO040",
    "Agder (NO042)": "NO042",
    "Rogaland (NO043)": "NO043",
    "Vestland (NO052)": "NO052",
    "Møre og Romsdal (NO060)": "NO060",
    "Trøndelag (NO070)": "NO070",
    "Nordland (NO071)": "NO071",
    "Troms og Finnmark (NO074)": "NO074",
}

section_header("🏢 Min leverandørprofil")

profil_id = st.session_state.get("profil_id")
if profil_id:
    st.success(f"Innlogget profil ID: {profil_id}")

with st.form("profil_form"):
    col1, col2 = st.columns(2)
    with col1:
        org_nr = st.text_input("Organisasjonsnummer *", placeholder="123456789")
        navn = st.text_input("Firmanavn *", placeholder="AS Mitt Firma")
        antall_ansatte = st.number_input("Antall ansatte", min_value=0, value=0)
    with col2:
        min_verdi = st.number_input(
            "Min. kontraktsverdi (NOK)", min_value=0, value=0, step=100000
        )
        max_verdi = st.number_input(
            "Maks. kontraktsverdi (NOK)", min_value=0, value=0, step=100000
        )
        sertifiseringer_input = st.text_input(
            "Sertifiseringer (komma-separert)", placeholder="ISO 9001, ISO 14001"
        )

    cpv_valgt = st.multiselect(
        "CPV-koder (hva tilbyr dere?)",
        options=list(VANLIGE_CPV.keys()),
        help="Velg de kategoriene som beskriver dine tjenester",
    )

    regioner_valgt = st.multiselect(
        "Aktuelle regioner",
        options=list(NUTS_REGIONER.keys()),
        default=["Hele Norge"],
    )

    submitted = st.form_submit_button("Lagre profil", type="primary")

    if submitted:
        if not org_nr or not navn:
            st.error("Organisasjonsnummer og firmanavn er obligatorisk.")
        else:
            cpv_koder = [VANLIGE_CPV[k] for k in cpv_valgt]
            nuts_regioner = [NUTS_REGIONER[r] for r in regioner_valgt if NUTS_REGIONER[r]]
            sertifiseringer = [
                s.strip() for s in sertifiseringer_input.split(",") if s.strip()
            ]

            payload = {
                "org_nr": org_nr,
                "navn": navn,
                "cpv_koder": cpv_koder,
                "nuts_regioner": nuts_regioner,
                "min_verdi": min_verdi if min_verdi > 0 else None,
                "max_verdi": max_verdi if max_verdi > 0 else None,
                "antall_ansatte": antall_ansatte if antall_ansatte > 0 else None,
                "sertifiseringer": sertifiseringer,
            }

            try:
                with httpx.Client(timeout=10) as client:
                    if profil_id:
                        resp = client.put(f"{API_BASE}/profil/{profil_id}", json=payload)
                    else:
                        resp = client.post(f"{API_BASE}/profil", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    st.session_state["profil_id"] = data["id"]
                    st.toast("Profil lagret!", icon="✅")
                    st.success(f"Profil lagret med ID: {data['id']}")
            except Exception as e:
                st.error(f"Feil ved lagring: {e}")
