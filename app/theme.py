import streamlit as st

NAVY = "#1F3A5F"
GOLD = "#B08D2E"
PAPER = "#F4F6F9"
SUCCESS = "#2ECC71"
WARNING = "#E67E22"
DANGER = "#C0392B"

STATUS_COLORS = {
    "NY": "#6C757D",
    "SETT": "#17A2B8",
    "INTERESSERT": "#1F3A5F",
    "FORKASTET": "#C0392B",
    "LEVERT": "#B08D2E",
    "VUNNET": "#27AE60",
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
            --paper: {PAPER};
        }}

        /* App background */
        .stApp {{
            background-color: {PAPER};
        }}

        /* Top bar */
        .stApp header {{
            background-color: {NAVY} !important;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: #162d4e;
        }}
        [data-testid="stSidebarNav"] {{
            border-top: 3px solid {GOLD};
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(176, 141, 46, 0.18);
            border-left: 3px solid {GOLD};
        }}

        /* Headings */
        h1, h2, h3 {{
            color: {NAVY};
            font-weight: 700;
        }}

        /* Eyebrow label */
        .eyebrow {{
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {GOLD};
            margin-bottom: 0.1rem;
            line-height: 1;
        }}

        /* Section header bar */
        .section-header {{
            background: linear-gradient(90deg, {NAVY} 0%, #2a4e7a 100%);
            color: white;
            padding: 0.65rem 1.2rem;
            border-radius: 6px;
            margin-bottom: 1.4rem;
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: 0.01em;
            border-left: 4px solid {GOLD};
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
            padding: 4px 16px;
            border-radius: 4px;
            color: white;
            font-weight: 700;
            font-size: 1em;
            letter-spacing: 0.03em;
        }}

        /* Card border polish */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 8px !important;
            border-color: #d1d9e6 !important;
            background: white;
        }}

        /* Primary buttons */
        .stButton > button[kind="primary"] {{
            background: {NAVY};
            border: none;
            border-bottom: 2px solid {GOLD};
            color: white;
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #2a4e7a;
            border-bottom-color: {GOLD};
        }}

        /* Metric value */
        [data-testid="stMetricValue"] {{
            color: {NAVY};
            font-weight: 700;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 2px solid {GOLD};
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {NAVY};
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom: 3px solid {GOLD} !important;
            color: {NAVY} !important;
        }}

        /* Expander headers */
        [data-testid="stExpander"] summary {{
            font-weight: 600;
            color: {NAVY};
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
