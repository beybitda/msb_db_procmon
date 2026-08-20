"""App-wide CSS theme. Pulled out of app.py so styling changes don't
require touching page logic.
"""
import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Background */
.stApp { background-color: #0D0F14; }
section[data-testid="stSidebar"] { background-color: #111318 !important; border-right: 1px solid #1E222D; }

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: #7A8099 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; }

section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div { background-color: #1A1D26 !important; border: 1px solid #2A2E3D !important; color: #C8CCDB !important; }

/* KPI cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.kpi-card {
    background: #111318;
    border: 1px solid #1E222D;
    border-radius: 4px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.success::before { background: #00D4A0; }
.kpi-card.failed::before  { background: #FF4757; }
.kpi-card.warning::before { background: #FFB627; }
.kpi-card.total::before   { background: #4A9EFF; }

.kpi-label { color: #4A5068; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.kpi-value { color: #E8EAF0; font-size: 32px; font-weight: 300; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.kpi-sub   { color: #3D4258; font-size: 11px; margin-top: 4px; }

/* Section headers */
.section-eyebrow {
    color: #4A5068;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-family: 'IBM Plex Mono', monospace;
    border-left: 2px solid #4A9EFF;
    padding-left: 10px;
    margin: 32px 0 16px;
}

/* Status pills */
.status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.05em;
}
.pill-success  { background: rgba(0,212,160,0.12); color: #00D4A0; border: 1px solid rgba(0,212,160,0.25); }
.pill-failed   { background: rgba(255,71,87,0.12);  color: #FF4757; border: 1px solid rgba(255,71,87,0.25); }
.pill-running  { background: rgba(74,158,255,0.12); color: #4A9EFF; border: 1px solid rgba(74,158,255,0.25); }
.pill-warning  { background: rgba(255,182,39,0.12); color: #FFB627; border: 1px solid rgba(255,182,39,0.25); }
.pill-skipped  { background: rgba(122,128,153,0.12);color: #7A8099; border: 1px solid rgba(122,128,153,0.25); }
.pill-timeout  { background: rgba(255,107,53,0.12); color: #FF6B35; border: 1px solid rgba(255,107,53,0.25); }
.pill-retrying { background: rgba(168,85,247,0.12); color: #A855F7; border: 1px solid rgba(168,85,247,0.25); }
.pill-created  { background: rgba(74,158,255,0.08); color: #4A9EFF; border: 1px solid rgba(74,158,255,0.15); }
.pill-cancelled{ background: rgba(122,128,153,0.12);color: #7A8099; border: 1px solid rgba(122,128,153,0.2); }

/* Table styling */
.stDataFrame { border: 1px solid #1E222D !important; border-radius: 4px; }
.stDataFrame thead th { background-color: #111318 !important; color: #4A5068 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 10px !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; border-bottom: 1px solid #1E222D !important; }
.stDataFrame tbody td { color: #C8CCDB !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; border-bottom: 1px solid #1A1D26 !important; background-color: #0D0F14 !important; }
.stDataFrame tbody tr:hover td { background-color: #111318 !important; }

/* App title */
.app-header { padding: 8px 0 24px; border-bottom: 1px solid #1E222D; margin-bottom: 0; }
.app-title { color: #E8EAF0; font-size: 22px; font-weight: 500; letter-spacing: -0.01em; }
.app-subtitle { color: #4A5068; font-size: 12px; font-family: 'IBM Plex Mono', monospace; margin-top: 2px; }

/* Refresh indicator */
.refresh-dot {
    display: inline-block;
    width: 6px; height: 6px;
    background: #00D4A0;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Error detail box */
.error-box {
    background: rgba(255,71,87,0.06);
    border: 1px solid rgba(255,71,87,0.2);
    border-radius: 4px;
    padding: 12px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #FF4757;
    margin: 8px 0;
    white-space: pre-wrap;
    word-break: break-all;
}

/* Sidebar logo */
.sidebar-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #4A9EFF;
    letter-spacing: 0.05em;
    padding: 16px 0 24px;
    border-bottom: 1px solid #1E222D;
    margin-bottom: 20px;
}

div[data-testid="stMetric"] { background: #111318; border: 1px solid #1E222D; border-radius: 4px; padding: 16px; }
div[data-testid="stMetric"] label { color: #4A5068 !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 0.1em; font-family: 'IBM Plex Mono', monospace; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #E8EAF0 !important; font-family: 'IBM Plex Mono', monospace; }

/* Plotly charts background */
.js-plotly-plot .plotly .bg { fill: #111318 !important; }

/* Button */
.stButton button {
    background-color: #1A1D26 !important;
    color: #C8CCDB !important;
    border: 1px solid #2A2E3D !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.05em !important;
    border-radius: 3px !important;
}
.stButton button:hover {
    border-color: #4A9EFF !important;
    color: #4A9EFF !important;
}

div[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #1E222D; gap: 0; }
div[data-baseweb="tab"] { background: transparent !important; color: #4A5068 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; padding: 8px 20px !important; border-radius: 0 !important; }
div[data-baseweb="tab"][aria-selected="true"] { color: #4A9EFF !important; border-bottom: 2px solid #4A9EFF !important; }
</style>
"""


def inject_custom_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
