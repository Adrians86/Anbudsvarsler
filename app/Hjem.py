"""Anbudsvarsler — Streamlit hovedapp."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Anbudsvarsler",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.theme import inject_css, section_header

inject_css()


st.sidebar.image(
    "https://via.placeholder.com/200x60/0A1F44/C9A84C?text=Anbudsvarsler",
    use_container_width=True,
)
st.sidebar.markdown("---")

section_header("📋 Anbudsvarsler", eyebrow="ANBUDSVARSLER")
st.markdown(
    "AI-drevet verktøy som hjelper private leverandører å finne, kvalifisere og følge opp "
    "offentlige anbud i Norge."
)

st.info(
    "Naviger til sidene i menyen til venstre for å komme i gang. "
    "Start med å opprette din **leverandørprofil**."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Sider tilgjengelig", "4")
with col2:
    st.metric("Datakilder", "Doffin + TED")
with col3:
    st.metric("Oppdatering", "Daglig kl. 06:00")
