"""Side 1 — Min profil."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime, timedelta

import httpx
import streamlit as st

from app.config import API_BASE_URL as API_BASE
from app.cpv_data import (
    CPV_GRUPPER, NUTS_REGIONER, SERTIFISERINGER_LISTE,
    DOKUMENT_KATEGORIER, DOKUMENT_UTLOEP_MÅNEDER, alle_oppslag,
)
from app.theme import inject_css, section_header

st.set_page_config(page_title="Min profil | Anbudsvarsler", page_icon="🏢", layout="wide")
inject_css()

section_header("🏢 Min leverandørprofil", eyebrow="MIN LEVERANDØRPROFIL")

# --- Tilkoblingsstatus ---
try:
    with httpx.Client(timeout=5) as _c:
        _c.get(f"{API_BASE}/health").raise_for_status()
    st.success(f"Backend tilkoblet: `{API_BASE}`")
except Exception as _e:
    st.error(
        f"**Backend ikke tilgjengelig** (`{API_BASE}`)\n\n"
        f"Feil: {_e}\n\n"
        "Sett `API_BASE_URL` i Streamlit Cloud → Settings → Secrets."
    )

profil_id = st.session_state.get("profil_id")
if profil_id:
    st.info(f"Profil ID: **{profil_id}**")

# --- Last eksisterende profil ---
_ALLE_CPV = alle_oppslag()

if profil_id and "profil_data" not in st.session_state:
    try:
        with httpx.Client(timeout=10) as _c:
            _r = _c.get(f"{API_BASE}/profil/{profil_id}")
            _r.raise_for_status()
            st.session_state.profil_data = _r.json()
    except Exception:
        st.session_state.profil_data = {}
elif "profil_data" not in st.session_state:
    st.session_state.profil_data = {}

pd = st.session_state.profil_data  # kortform

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Firmadata",
    "🏷️ Bransjeprofil",
    "✅ Sertifiseringer",
    "📎 Referanser",
    "📂 Dokumenter",
])

# ==================== TAB 1: FIRMADATA ====================
with tab1:
    # Brønnøysund-oppslag
    st.markdown("#### Organisasjonsoppslag")
    col_orgnr, col_btn = st.columns([3, 1])
    with col_orgnr:
        orgnr_input = st.text_input(
            "Organisasjonsnummer for oppslag",
            value=pd.get("org_nr", ""),
            placeholder="123456789",
            key="orgnr_lookup_input",
        )
    with col_btn:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        if st.button("🔍 Hent fra Brønnøysund", use_container_width=True):
            clean = "".join(c for c in orgnr_input if c.isdigit())
            if len(clean) == 9:
                try:
                    with httpx.Client(timeout=8) as _c:
                        _r = _c.get(f"https://data.brreg.no/enhetsregisteret/api/enheter/{clean}")
                        _r.raise_for_status()
                        _bdata = _r.json()
                    _adr = _bdata.get("forretningsadresse", {})
                    st.session_state.profil_data.update({
                        "org_nr": clean,
                        "navn": _bdata.get("navn", ""),
                        "organisasjonsform": _bdata.get("organisasjonsform", {}).get("beskrivelse", ""),
                        "adresse": ", ".join(_adr.get("adresse", [])),
                        "postnr": str(_adr.get("postnummer", "")),
                        "sted": _adr.get("poststed", ""),
                        "antall_ansatte": _bdata.get("antallAnsatte"),
                    })
                    pd = st.session_state.profil_data
                    st.toast(f"Hentet: {pd['navn']}", icon="✅")
                    st.rerun()
                except httpx.HTTPStatusError:
                    st.error("Organisasjonsnummeret ble ikke funnet i Brønnøysundregisteret.")
                except Exception as _e:
                    st.error(f"Brreg-oppslag feilet: {_e}")
            else:
                st.error("Oppgi et gyldig 9-sifret organisasjonsnummer.")

    st.divider()

    with st.form("firmadata_form"):
        col1, col2 = st.columns(2)
        with col1:
            org_nr = st.text_input("Organisasjonsnummer *", value=pd.get("org_nr", ""), placeholder="123456789")
            navn = st.text_input("Firmanavn *", value=pd.get("navn", ""), placeholder="AS Mitt Firma")
            organisasjonsform = st.text_input("Organisasjonsform", value=pd.get("organisasjonsform", ""), placeholder="Aksjeselskap")
            antall_ansatte = st.number_input("Antall ansatte", min_value=0, value=pd.get("antall_ansatte") or 0)
            aarlig_omsetning = st.number_input(
                "Årlig omsetning (NOK)",
                min_value=0,
                value=pd.get("aarlig_omsetning_nok") or 0,
                step=500000,
                help="Brukes i finansiell kapasitetssjekk (§16-4)",
            )
        with col2:
            kontaktperson = st.text_input("Kontaktperson", value=pd.get("kontaktperson", ""), placeholder="Ola Nordmann")
            epost = st.text_input("E-post", value=pd.get("epost", ""), placeholder="post@firma.no")
            telefon = st.text_input("Telefon", value=pd.get("telefon", ""), placeholder="+47 12 34 56 78")
            nettsted = st.text_input("Nettsted", value=pd.get("nettsted", ""), placeholder="https://firma.no")
            adresse = st.text_input("Adresse", value=pd.get("adresse", ""), placeholder="Storgata 1")
            col_pnr, col_sted = st.columns(2)
            with col_pnr:
                postnr = st.text_input("Postnummer", value=pd.get("postnr", ""), placeholder="0150")
            with col_sted:
                sted = st.text_input("Poststed", value=pd.get("sted", ""), placeholder="Oslo")

        submitted = st.form_submit_button("💾 Lagre firmadata", type="primary")

        if submitted:
            if not org_nr or not navn:
                st.error("Organisasjonsnummer og firmanavn er obligatorisk.")
            else:
                payload = {
                    "org_nr": org_nr,
                    "navn": navn,
                    "kontaktperson": kontaktperson or None,
                    "epost": epost or None,
                    "telefon": telefon or None,
                    "nettsted": nettsted or None,
                    "adresse": adresse or None,
                    "postnr": postnr or None,
                    "sted": sted or None,
                    "organisasjonsform": organisasjonsform or None,
                    "antall_ansatte": antall_ansatte if antall_ansatte > 0 else None,
                    "aarlig_omsetning_nok": aarlig_omsetning if aarlig_omsetning > 0 else None,
                    "cpv_koder": pd.get("cpv_koder", []),
                    "nuts_regioner": pd.get("nuts_regioner", []),
                    "sertifiseringer": pd.get("sertifiseringer", []),
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
                        st.session_state.profil_data.update(data)
                        st.toast("Firmadata lagret!", icon="✅")
                        st.rerun()
                except Exception as e:
                    st.error(f"Feil ved lagring: {e}")

# ==================== TAB 2: BRANSJEPROFIL ====================
with tab2:
    with st.form("bransjeprofil_form"):
        st.markdown("**CPV-koder (hva tilbyr dere?)**")
        cpv_valgt: list[str] = []
        for bransje, koder in CPV_GRUPPER.items():
            eksisterende = [k for k in pd.get("cpv_koder", [])
                            if any(k == _ALLE_CPV.get(s) for s in koder)]
            forhåndsvalgt = [s for s in koder if _ALLE_CPV.get(s) in pd.get("cpv_koder", [])]
            with st.expander(bransje):
                valgte = st.multiselect(
                    f"Velg fra {bransje}",
                    options=koder,
                    default=forhåndsvalgt,
                    label_visibility="collapsed",
                    key=f"cpv2_{bransje}",
                )
                cpv_valgt.extend(valgte)

        st.divider()

        st.markdown("**Geografisk dekning (NUTS-regioner)**")
        eksist_nuts_labels = [lbl for lbl, kode in NUTS_REGIONER.items()
                               if kode in pd.get("nuts_regioner", [])]
        if not eksist_nuts_labels:
            eksist_nuts_labels = ["Hele Norge"]
        regioner_valgt = st.multiselect(
            "Aktuelle regioner",
            options=list(NUTS_REGIONER.keys()),
            default=eksist_nuts_labels,
            label_visibility="collapsed",
        )

        st.divider()

        col_min, col_max, col_pref = st.columns(3)
        with col_min:
            min_verdi = st.number_input(
                "Min. kontraktsverdi (NOK)",
                min_value=0,
                value=int(pd.get("min_verdi") or 0),
                step=100_000,
            )
        with col_max:
            max_verdi = st.number_input(
                "Maks. kontraktsverdi (NOK)",
                min_value=0,
                value=int(pd.get("max_verdi") or 0),
                step=500_000,
            )
        with col_pref:
            pref_options = ["begge", "rammeavtale", "enkelt"]
            pref_idx = pref_options.index(pd.get("kontrakt_preferanse", "begge"))
            kontrakt_pref = st.selectbox(
                "Foretrekker kontraktstype",
                options=pref_options,
                index=pref_idx,
                format_func=lambda x: {"begge": "Begge typer", "rammeavtale": "Rammeavtaler", "enkelt": "Enkeltkontrakter"}[x],
            )

        submitted2 = st.form_submit_button("💾 Lagre bransjeprofil", type="primary")

        if submitted2:
            if not profil_id:
                st.warning("Lagre firmadata i Tab 1 først for å opprette profilen.")
            else:
                cpv_koder = list({_ALLE_CPV[k] for k in cpv_valgt if k in _ALLE_CPV})
                nuts_koder = [NUTS_REGIONER[r] for r in regioner_valgt if NUTS_REGIONER[r]]
                existing = dict(pd)
                existing.update({
                    "cpv_koder": cpv_koder,
                    "nuts_regioner": nuts_koder,
                    "min_verdi": min_verdi if min_verdi > 0 else None,
                    "max_verdi": max_verdi if max_verdi > 0 else None,
                    "kontrakt_preferanse": kontrakt_pref,
                })
                try:
                    with httpx.Client(timeout=10) as client:
                        resp = client.put(f"{API_BASE}/profil/{profil_id}", json=existing)
                        resp.raise_for_status()
                        st.session_state.profil_data.update({"cpv_koder": cpv_koder, "nuts_regioner": nuts_koder})
                        st.toast("Bransjeprofil lagret!", icon="✅")
                        st.rerun()
                except Exception as e:
                    st.error(f"Feil ved lagring: {e}")

# ==================== TAB 3: SERTIFISERINGER ====================
with tab3:
    with st.form("sertifiseringer_form"):
        st.markdown("Velg alle sertifiseringer og godkjenninger dere har:")
        eksist_sert = pd.get("sertifiseringer", [])
        valgte_sert = st.multiselect(
            "Sertifiseringer",
            options=SERTIFISERINGER_LISTE,
            default=[s for s in eksist_sert if s in SERTIFISERINGER_LISTE],
            label_visibility="collapsed",
        )
        andre = st.text_input(
            "Andre sertifiseringer (komma-separert)",
            value=", ".join(s for s in eksist_sert if s not in SERTIFISERINGER_LISTE),
            placeholder="Spesiell bransjesertifisering...",
        )
        submitted3 = st.form_submit_button("💾 Lagre sertifiseringer", type="primary")

        if submitted3:
            if not profil_id:
                st.warning("Lagre firmadata i Tab 1 først.")
            else:
                alle_sert = list(valgte_sert)
                if andre:
                    alle_sert += [s.strip() for s in andre.split(",") if s.strip()]
                existing = dict(pd)
                existing["sertifiseringer"] = alle_sert
                try:
                    with httpx.Client(timeout=10) as client:
                        resp = client.put(f"{API_BASE}/profil/{profil_id}", json=existing)
                        resp.raise_for_status()
                        st.session_state.profil_data["sertifiseringer"] = alle_sert
                        st.toast("Sertifiseringer lagret!", icon="✅")
                except Exception as e:
                    st.error(f"Feil: {e}")

# ==================== TAB 4: REFERANSEPROSJEKTER ====================
with tab4:
    if not profil_id:
        st.warning("Lagre firmadata i Tab 1 først.")
    else:
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{API_BASE}/referanse/{profil_id}")
                resp.raise_for_status()
                referanser = resp.json()
        except Exception as e:
            st.error(f"Kunne ikke hente referanser: {e}")
            referanser = []

        st.markdown(f"**{len(referanser)} referanseprosjekt(er) registrert**")
        for ref in referanser:
            with st.expander(f"📎 {ref.get('prosjektnavn', 'Ukjent')} — {ref.get('oppdragsgiver_navn', '')}"):
                col_a, col_b, col_slett = st.columns([3, 3, 1])
                with col_a:
                    st.caption(f"Periode: {ref.get('periode_fra', '?')} – {ref.get('periode_til', '?')}")
                    if ref.get("kontraktsverdi_nok"):
                        st.caption(f"Verdi: {ref['kontraktsverdi_nok']:,} NOK".replace(",", " "))
                    if ref.get("cpv"):
                        st.caption(f"CPV: {ref['cpv']}")
                with col_b:
                    if ref.get("beskrivelse"):
                        st.caption(ref["beskrivelse"][:200])
                    if ref.get("kontaktperson"):
                        st.caption(f"Kontakt: {ref['kontaktperson']} {ref.get('kontakttelefon', '')}")
                with col_slett:
                    if st.button("🗑️", key=f"slett_ref_{ref['id']}", help="Slett referanse"):
                        try:
                            with httpx.Client(timeout=10) as client:
                                client.delete(f"{API_BASE}/referanse/{ref['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Feil: {e}")

        st.divider()
        with st.expander("➕ Legg til nytt referanseprosjekt"):
            with st.form("ny_referanse"):
                col_a, col_b = st.columns(2)
                with col_a:
                    prosjektnavn = st.text_input("Prosjektnavn *", placeholder="System-utvikling for NAV")
                    oppdragsgiver = st.text_input("Oppdragsgiver *", placeholder="NAV")
                    oppdragsgiver_orgnr = st.text_input("Oppdragsgivers org.nr", placeholder="889640782")
                    kontraktsverdi = st.number_input("Kontraktsverdi (NOK)", min_value=0, step=100_000)
                with col_b:
                    periode_fra = st.text_input("Periode fra", placeholder="2023-01")
                    periode_til = st.text_input("Periode til", placeholder="2024-06")
                    cpv_ref = st.text_input("CPV-kode", placeholder="72200000")
                    kontakt_navn = st.text_input("Kontaktperson", placeholder="Kari Nordmann")
                    kontakt_tlf = st.text_input("Kontakttelefon", placeholder="+47 ...")
                beskrivelse = st.text_area("Kort beskrivelse (maks 500 tegn)", max_chars=500)
                kan_kontaktes = st.checkbox("Oppdragsgiver kan kontaktes", value=True)

                if st.form_submit_button("Legg til referanse", type="primary"):
                    if prosjektnavn and oppdragsgiver:
                        try:
                            with httpx.Client(timeout=10) as client:
                                client.post(f"{API_BASE}/referanse", json={
                                    "profil_id": profil_id,
                                    "prosjektnavn": prosjektnavn,
                                    "oppdragsgiver_navn": oppdragsgiver,
                                    "oppdragsgiver_org_nr": oppdragsgiver_orgnr or None,
                                    "kontraktsverdi_nok": kontraktsverdi if kontraktsverdi > 0 else None,
                                    "periode_fra": periode_fra or None,
                                    "periode_til": periode_til or None,
                                    "cpv": cpv_ref or None,
                                    "beskrivelse": beskrivelse or None,
                                    "kontaktperson": kontakt_navn or None,
                                    "kontakttelefon": kontakt_tlf or None,
                                    "kan_kontaktes": kan_kontaktes,
                                })
                            st.toast("Referanse lagt til!", icon="✅")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Feil: {e}")
                    else:
                        st.error("Prosjektnavn og oppdragsgiver er obligatorisk.")

# ==================== TAB 5: DOKUMENTBIBLIOTEK ====================
with tab5:
    if not profil_id:
        st.warning("Lagre firmadata i Tab 1 først.")
    else:
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{API_BASE}/dokument/{profil_id}")
                resp.raise_for_status()
                dokumenter = resp.json()
        except Exception as e:
            st.error(f"Kunne ikke hente dokumenter: {e}")
            dokumenter = []

        nå = datetime.utcnow()

        def _dokument_status(dok: dict) -> tuple[str, str]:
            if not dok.get("lastet_opp"):
                return "⬜", "Ikke lastet opp"
            utloep = dok.get("utloep_dato")
            if not utloep:
                return "✅", "Lastet opp"
            try:
                utloep_dt = datetime.fromisoformat(utloep[:19])
            except ValueError:
                return "✅", "Lastet opp"
            dager = (utloep_dt - nå).days
            if dager < 0:
                return "🔴", f"UTLØPT ({abs(dager)} dager siden)"
            if dager <= 30:
                return "🟡", f"Utløper om {dager} dager"
            return "✅", f"Gyldig til {utloep[:10]}"

        # Vis eksisterende dokumenter
        if dokumenter:
            st.markdown(f"**{len(dokumenter)} dokument(er) registrert**")
            for dok in dokumenter:
                ikon, status_tekst = _dokument_status(dok)
                kat_navn = DOKUMENT_KATEGORIER.get(dok.get("kategori", "annet"), dok.get("kategori", ""))
                with st.container(border=True):
                    col_ikon, col_info, col_oppdater, col_slett = st.columns([1, 5, 3, 1])
                    with col_ikon:
                        st.markdown(f"### {ikon}")
                    with col_info:
                        st.markdown(f"**{dok.get('tittel', kat_navn)}**")
                        st.caption(f"{kat_navn} · {status_tekst}")
                    with col_oppdater:
                        ny_utloep = st.date_input(
                            "Ny utløpsdato",
                            value=None,
                            key=f"utloep_{dok['id']}",
                            label_visibility="collapsed",
                        )
                        if st.button("Marker som lastet opp", key=f"opp_{dok['id']}", use_container_width=True):
                            try:
                                oppdatering = {"lastet_opp": True}
                                if ny_utloep:
                                    oppdatering["utloep_dato"] = str(ny_utloep)
                                with httpx.Client(timeout=10) as client:
                                    client.put(f"{API_BASE}/dokument/{dok['id']}", json=oppdatering)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Feil: {e}")
                    with col_slett:
                        if st.button("🗑️", key=f"slett_dok_{dok['id']}", help="Slett"):
                            try:
                                with httpx.Client(timeout=10) as client:
                                    client.delete(f"{API_BASE}/dokument/{dok['id']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Feil: {e}")
        else:
            st.info("Ingen dokumenter registrert ennå.")

        # Legg til standard dokumentsett
        st.divider()
        col_std, col_ny = st.columns([2, 1])
        with col_std:
            if st.button("Opprett standard dokumentsett", use_container_width=True,
                         help="Legger til alle standarddokumenter som tomme plasser"):
                eksist_kat = {d.get("kategori") for d in dokumenter}
                nye = 0
                try:
                    with httpx.Client(timeout=15) as client:
                        for kat, tittel in DOKUMENT_KATEGORIER.items():
                            if kat not in eksist_kat:
                                utloep_mnd = DOKUMENT_UTLOEP_MÅNEDER.get(kat)
                                utloep = None
                                if utloep_mnd:
                                    utloep = (nå + timedelta(days=30 * utloep_mnd)).isoformat()
                                client.post(f"{API_BASE}/dokument", json={
                                    "profil_id": profil_id,
                                    "kategori": kat,
                                    "tittel": tittel,
                                    "lastet_opp": False,
                                    "utloep_dato": utloep,
                                })
                                nye += 1
                    st.toast(f"{nye} dokumenter lagt til!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Feil: {e}")

        with col_ny:
            with st.expander("➕ Legg til dokument"):
                with st.form("nytt_dok"):
                    kat = st.selectbox("Kategori", options=list(DOKUMENT_KATEGORIER.keys()),
                                       format_func=lambda k: DOKUMENT_KATEGORIER[k])
                    tittel = st.text_input("Tittel")
                    utloep_dato = st.date_input("Utløpsdato (valgfritt)", value=None)
                    lastet_opp = st.checkbox("Allerede lastet opp / tilgjengelig")
                    if st.form_submit_button("Legg til"):
                        try:
                            with httpx.Client(timeout=10) as client:
                                client.post(f"{API_BASE}/dokument", json={
                                    "profil_id": profil_id,
                                    "kategori": kat,
                                    "tittel": tittel or DOKUMENT_KATEGORIER[kat],
                                    "lastet_opp": lastet_opp,
                                    "utloep_dato": str(utloep_dato) if utloep_dato else None,
                                })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Feil: {e}")
