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
            --light-bg: {LIGHT_BG};
        }}

        /* Top bar */
        .stApp header {{
            background-color: {NAVY} !important;
        }}

        /* Sidebar nav accent */
        [data-testid="stSidebarNav"] {{
            border-top: 3px solid {GOLD};
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(201, 168, 76, 0.15);
            border-left: 3px solid {GOLD};
        }}

        /* Headings */
        h1, h2, h3 {{
            color: {NAVY};
        }}

        /* Section header bar */
        .section-header {{
            background: linear-gradient(90deg, {NAVY} 0%, #163264 100%);
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            margin-bottom: 1.2rem;
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: 0.01em;
            border-left: 4px solid {GOLD};
        }}

        /* Eyebrow label above section headers */
        .eyebrow {{
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {GOLD};
            margin-bottom: 0.15rem;
        }}

        /* Status pills */
        .status-pill {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            color: white;
            font-size: 0.78em;
            font-weight: 600;
        }}

        /* GO/NO-GO badges */
        .resultat-badge {{
            display: inline-block;
            padding: 4px 14px;
            border-radius: 4px;
            color: white;
            font-weight: 700;
            font-size: 1em;
        }}

        /* Card containers */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 8px !important;
            border-color: #DDE3ED !important;
        }}

        /* Primary buttons */
        .stButton > button[kind="primary"] {{
            background: {NAVY};
            border: none;
            border-bottom: 2px solid {GOLD};
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #163264;
        }}

        /* Metric value color */
        [data-testid="stMetricValue"] {{
            color: {NAVY};
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(text: str, eyebrow: str = ""):
    eye = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    st.markdown(
        f'{eye}<div class="section-header">{text}</div>',
        unsafe_allow_html=True,
    )


def status_pill(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6C757D")
    return f'<span class="status-pill" style="background:{color}">{status}</span>'


def resultat_badge(resultat: str) -> str:
    color = RESULTAT_COLORS.get(resultat, "#6C757D")
    return f'<span class="resultat-badge" style="background:{color}">{resultat}</span>'
