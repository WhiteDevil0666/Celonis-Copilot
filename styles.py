"""
components/styles.py
Single source of truth for all custom CSS.
Import and call inject_css() once at app startup.
"""

import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

/* ── BASE ── */
html, body { background:#0b0e1a !important; color:#e8ecf4 !important; }
[data-testid="stAppViewContainer"],[data-testid="stMain"],.main,section.main,.block-container {
    background:#0b0e1a !important; color:#e8ecf4 !important;
    font-family:'Sora',sans-serif !important;
    padding-top:0.8rem !important; max-width:100% !important;
}
#MainMenu,footer,header,[data-testid="stHeader"],
[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"] {
    display:none !important;
}
[data-testid="stSidebar"] { display:none !important; }

p,span,li,div,label,h1,h2,h3,h4,h5,h6,
.stMarkdown,[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color:#e8ecf4 !important; }

/* ── INPUTS ── */
[data-testid="stTextInput"] input,[data-baseweb="select"]>div {
    background:#1a2340 !important; color:#e8ecf4 !important;
    border:1px solid #2a3a5c !important; border-radius:8px !important;
    font-family:'Sora',sans-serif !important; font-size:13px !important;
}
[data-testid="stTextInput"] input::placeholder { color:#7a8aab !important; }
[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label { color:#c8d4e8 !important; font-size:12px !important; }
[data-baseweb="popover"] ul,[data-baseweb="menu"] ul { background:#1a2340 !important; }
[data-baseweb="popover"] li,[data-baseweb="menu"] li { color:#e8ecf4 !important; }
[data-baseweb="popover"] li:hover,[data-baseweb="menu"] li:hover { background:#2a3a5c !important; }

/* ── BUTTONS ── */
.stButton>button {
    background:rgba(255,255,255,0.04) !important; border:1px solid #2a3a5c !important;
    color:#c8d4e8 !important; font-family:'Sora',sans-serif !important;
    font-size:12px !important; text-align:left !important; border-radius:8px !important;
    padding:9px 12px !important; width:100% !important; white-space:normal !important;
    height:auto !important; line-height:1.5 !important; margin-bottom:3px !important;
    transition:all 0.18s !important;
}
.stButton>button:hover {
    background:rgba(47,110,245,0.18) !important; border-color:#2f6ef5 !important; color:#fff !important;
}

/* ── ALERTS ── */
.stAlert { border-radius:8px !important; background:#1a2340 !important; }
.stAlert p,[data-testid="stNotification"] p { color:#e8ecf4 !important; font-size:12px !important; }

/* ── METRIC ── */
[data-testid="stMetric"] label { color:#9ab0cc !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#00d4b4 !important; font-size:18px !important; }

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] { background:#111627 !important; border-radius:10px !important; }
[data-testid="stTabs"] [data-baseweb="tab"] { color:#9ab0cc !important; font-family:'Sora',sans-serif !important; }
[data-testid="stTabs"] [aria-selected="true"] { color:#fff !important; background:#2f6ef5 !important; border-radius:8px !important; }

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background:#141b2d !important; border:1px solid #2a3a5c !important;
    border-radius:14px !important; padding:14px 18px !important; margin-bottom:10px !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
    color:#e8ecf4 !important; font-size:14px !important; line-height:1.8 !important;
}
[data-testid="stChatMessage"] h1,[data-testid="stChatMessage"] h2,[data-testid="stChatMessage"] h3 {
    color:#7dd3fc !important; font-weight:700 !important; margin-top:16px !important;
}
[data-testid="stChatMessage"] strong { color:#c8d8ff !important; }
[data-testid="stChatMessage"] code {
    background:#1e2d4a !important; color:#00d4b4 !important;
    padding:2px 7px !important; border-radius:5px !important;
    font-family:'Space Mono',monospace !important; font-size:12.5px !important;
}
[data-testid="stChatMessage"] pre {
    background:#0d1525 !important; border:1px solid #2a3a5c !important;
    border-radius:10px !important; padding:16px !important; overflow-x:auto !important;
}
[data-testid="stChatMessage"] pre code {
    background:none !important; color:#a5d6ff !important; padding:0 !important; font-size:13px !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"]>div,[data-testid="stChatInput"] {
    background:#141b2d !important; border:1px solid #2a3a5c !important; border-radius:14px !important;
}
[data-testid="stChatInput"] textarea {
    background:#141b2d !important; color:#e8ecf4 !important;
    font-family:'Sora',sans-serif !important; font-size:14px !important; caret-color:#2f6ef5 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color:#7a8aab !important; }

/* ── PROGRESS BAR ── */
[data-testid="stProgressBar"]>div { background:#1a2340 !important; border-radius:10px !important; }
[data-testid="stProgressBar"]>div>div { background:linear-gradient(90deg,#2f6ef5,#00d4b4) !important; border-radius:10px !important; }

/* ── FORMS ── */
[data-testid="stForm"] { background:#111627 !important; border:1px solid #2a3a5c !important; border-radius:12px !important; padding:16px !important; }

/* ── HEADER ── */
.celonis-header {
    background:linear-gradient(135deg,#141b2d,#1a2340);
    border:1px solid #2a3a5c; border-radius:14px;
    padding:14px 20px; margin-bottom:14px;
    display:flex; align-items:center; justify-content:space-between;
}
.header-left { display:flex; align-items:center; gap:12px; }
.header-icon { font-size:28px; }
.header-title { font-size:18px; font-weight:700; color:#fff; margin:0; }
.header-sub { font-size:11px; color:#7dd3fc; font-family:'Space Mono',monospace; margin:2px 0 0; }
.status-badge {
    display:flex; align-items:center; gap:7px;
    font-size:11px; color:#00d4b4; font-family:'Space Mono',monospace; font-weight:700;
    background:rgba(0,212,180,0.1); border:1px solid rgba(0,212,180,0.3);
    border-radius:20px; padding:5px 14px;
}
.dot-live {
    width:7px; height:7px; background:#00d4b4; border-radius:50%;
    box-shadow:0 0 7px #00d4b4; display:inline-block; animation:blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* ── WELCOME BOX ── */
.welcome-box {
    text-align:center; padding:48px 20px;
    background:linear-gradient(135deg,#141b2d,#1a2340);
    border:1px solid #2a3a5c; border-radius:18px; margin:10px 0 20px;
}
.welcome-title { font-size:22px; font-weight:700; color:#fff; margin-bottom:10px; }
.welcome-title span { color:#ff6d29; }
.welcome-sub { font-size:13.5px; color:#9ab0cc; max-width:500px; margin:0 auto; line-height:1.9; }
.welcome-sub em { color:#7dd3fc; font-style:normal; font-weight:600; }

/* ── BADGES ── */
.badge-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
.badge {
    border-radius:20px; padding:5px 14px; font-size:11px;
    font-family:'Space Mono',monospace; font-weight:700; display:inline-flex; align-items:center; gap:5px;
}
.badge-blue  { background:rgba(47,110,245,0.15); border:1px solid rgba(47,110,245,0.4); color:#7dd3fc; }
.badge-green { background:rgba(0,212,180,0.12);  border:1px solid rgba(0,212,180,0.35);  color:#00d4b4; }
.badge-orange{ background:rgba(255,109,41,0.12); border:1px solid rgba(255,109,41,0.35); color:#ff9a56; }

/* ── PANEL DIVIDER ── */
.panel-divider { height:1px; background:#2a3a5c; margin:14px 0; }
.panel-section-label {
    font-size:9px; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#7a8aab; font-family:'Space Mono',monospace; margin-bottom:8px;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0b0e1a; }
::-webkit-scrollbar-thumb { background:#2a3a5c; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#2f6ef5; }
</style>
""", unsafe_allow_html=True)
