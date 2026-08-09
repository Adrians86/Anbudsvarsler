import streamlit as st

NAVY = "#0A1F44"
GOLD = "#C9A84C"
LIGHT_BG = "#F4F6FA"
SUCCESS = "#2ECC71"
WARNING = "#F39C12"
DANGER = "#E74C3C"

STATUS_COLORS = {
    "NY": "#6C757D",
    "SETT": "#17A2B8",
    "INTERESSERT": "#007BFF",
    "FORKASTET": "#E74C3C",
    "LEVERT": "#FFC107",
    "VUNNET": "#28A745",
    "TAPT": "#6C757D",
}

RESULTAT_COLORS = {
    "GO": SUCCESS,
    "NO-GO": DANGER,
    "GÅ VIDERE MED FORBEHOLD": WARNING,
}


def inject_css():
    st.markdown(
        f"""
        <style>
        :root {{
            --navy: {NAVY};
            --gold: {GOLD};
        }}
        .stApp header {{
            background-color: {NAVY} !important;
        }}
        h1, h2, h3 {{
            color: {NAVY};
        }}
        .section-header {{
            background: {NAVY};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            font-weight: 600;
        }}
        .status-pill {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            color: white;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .resultat-badge {{
            display: inline-block;
            padding: 4px 14px;
            border-radius: 4px;
            color: white;
            font-weight: 700;
            font-size: 1em;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def status_pill(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6C757D")
    return f'<span class="status-pill" style="background:{color}">{status}</span>'


def resultat_badge(resultat: str) -> str:
    color = RESULTAT_COLORS.get(resultat, "#6C757D")
    return f'<span class="resultat-badge" style="background:{color}">{resultat}</span>'
