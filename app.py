"""
Celonis AI Agent — Single-file SaaS app
Changes:
  - API keys from secrets only (no input fields shown)
  - Toggle button (☰ / ✕) to open/close left panel
  - Chat input pinned to bottom, messages scroll above it
"""

import time
import sys
from collections import deque
import streamlit as st
from groq import Groq
import groq as groq_errors

# ══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Celonis AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════
#  OPTIONAL IMPORTS
# ══════════════════════════════════════════════════════════════════
try:
    import tiktoken
    _ENCODER  = tiktoken.get_encoding("cl100k_base")
    TIKTOKEN_OK = True
except Exception:
    TIKTOKEN_OK = False

try:
    from tavily import TavilyClient
    TAVILY_OK = True
except Exception:
    TAVILY_OK = False

try:
    from loguru import logger as _loguru
    import os; os.makedirs("logs", exist_ok=True)
    _loguru.remove()
    _loguru.add(sys.stdout, level="INFO",
                format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    _loguru.add("logs/app_{time:YYYY-MM-DD}.log", level="DEBUG",
                rotation="00:00", retention="14 days", compression="zip", enqueue=True)
    _loguru.add("logs/errors.log", level="ERROR",
                rotation="10 MB", retention="30 days", enqueue=True)
    LOGURU_OK = True
except Exception:
    LOGURU_OK = False

def _log(level: str, msg: str):
    if LOGURU_OK:
        getattr(_loguru, level)(msg)

# ══════════════════════════════════════════════════════════════════
#  SESSION STATE DEFAULTS
# ══════════════════════════════════════════════════════════════════
if "messages"     not in st.session_state: st.session_state.messages     = []
if "prefill"      not in st.session_state: st.session_state.prefill      = None
if "panel_open"   not in st.session_state: st.session_state.panel_open   = True
if "token_stats"  not in st.session_state: st.session_state.token_stats  = {"total":0,"prompt":0,"response":0,"turns":0}
if "rl_timestamps" not in st.session_state: st.session_state.rl_timestamps = deque()
if "rl_tier"      not in st.session_state: st.session_state.rl_tier      = "free"

# ══════════════════════════════════════════════════════════════════
#  API KEYS  — from secrets only, never shown in UI
# ══════════════════════════════════════════════════════════════════
GROQ_KEY   = st.secrets.get("GROQ_API_KEY",   "")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY",  "")

# ══════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

/* ── base ── */
html, body { background:#0b0e1a !important; color:#e8ecf4 !important; }
[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],.main,section.main,.block-container {
    background:#0b0e1a !important; color:#e8ecf4 !important;
    font-family:'Sora',sans-serif !important;
    padding-top:0 !important; max-width:100% !important;
}
#MainMenu,footer,header,[data-testid="stHeader"],
[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"] { display:none !important; }
[data-testid="stSidebar"] { display:none !important; }

p,span,li,div,label,h1,h2,h3,h4,h5,h6,
.stMarkdown,[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color:#e8ecf4 !important; }

/* ── inputs / selects ── */
[data-testid="stTextInput"] input,[data-baseweb="select"]>div {
    background:#1a2340 !important; color:#e8ecf4 !important;
    border:1px solid #2a3a5c !important; border-radius:8px !important;
    font-family:'Sora',sans-serif !important; font-size:13px !important;
}
[data-testid="stTextInput"] input::placeholder { color:#7a8aab !important; }
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label { color:#c8d4e8 !important; font-size:12px !important; }
[data-baseweb="popover"] ul,[data-baseweb="menu"] ul { background:#1a2340 !important; }
[data-baseweb="popover"] li,[data-baseweb="menu"] li { color:#e8ecf4 !important; }
[data-baseweb="popover"] li:hover,[data-baseweb="menu"] li:hover { background:#2a3a5c !important; }

/* ── buttons (global) ── */
.stButton>button {
    background:rgba(255,255,255,0.05) !important; border:1px solid #2a3a5c !important;
    color:#c8d4e8 !important; font-family:'Sora',sans-serif !important;
    font-size:12px !important; text-align:left !important; border-radius:8px !important;
    padding:9px 12px !important; width:100% !important; white-space:normal !important;
    height:auto !important; line-height:1.5 !important; margin-bottom:3px !important;
    transition:all 0.18s !important;
}
.stButton>button:hover {
    background:rgba(47,110,245,0.2) !important; border-color:#2f6ef5 !important; color:#fff !important;
}

/* ── toggle button  — small square, top-left ── */
div[data-testid="column"]:first-child .stButton:first-child > button {
    width:38px !important; height:38px !important; min-width:38px !important;
    padding:0 !important; font-size:18px !important; text-align:center !important;
    border-radius:10px !important; background:#1a2340 !important;
    border:1px solid #2a3a5c !important; color:#e8ecf4 !important;
    margin-bottom:0 !important; line-height:38px !important;
}
div[data-testid="column"]:first-child .stButton:first-child > button:hover {
    background:#2f6ef5 !important; border-color:#2f6ef5 !important;
}

/* ── alerts ── */
.stAlert { border-radius:8px !important; background:#1a2340 !important; }
.stAlert p,[data-testid="stNotification"] p { color:#e8ecf4 !important; font-size:12px !important; }

/* ── metric ── */
[data-testid="stMetric"] label { color:#9ab0cc !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#00d4b4 !important; font-size:18px !important; }

/* ── progress bar ── */
[data-testid="stProgressBar"]>div { background:#1a2340 !important; border-radius:10px !important; }
[data-testid="stProgressBar"]>div>div { background:linear-gradient(90deg,#2f6ef5,#00d4b4) !important; border-radius:10px !important; }

/* ── chat messages ── */
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
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 { color:#7dd3fc !important; font-weight:700 !important; margin-top:16px !important; }
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

/* ── chat input — pinned to bottom ── */
[data-testid="stChatInput"]>div,[data-testid="stChatInput"] {
    background:#141b2d !important; border:1px solid #2a3a5c !important; border-radius:14px !important;
}
[data-testid="stChatInput"] textarea {
    background:#141b2d !important; color:#e8ecf4 !important;
    font-family:'Sora',sans-serif !important; font-size:14px !important; caret-color:#2f6ef5 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color:#7a8aab !important; }

/* keep chat input wrapper always at bottom */
[data-testid="stBottom"] {
    background:#0b0e1a !important;
    border-top: 1px solid #1a2340 !important;
    padding: 10px 0 !important;
}

/* ── page header bar ── */
.cel-header {
    background:linear-gradient(135deg,#141b2d,#1a2340);
    border:1px solid #2a3a5c; border-radius:14px;
    padding:12px 18px; margin-bottom:12px;
    display:flex; align-items:center; justify-content:space-between;
}
.cel-header-left { display:flex; align-items:center; gap:12px; }
.cel-title { font-size:17px; font-weight:700; color:#fff; margin:0; }
.cel-sub { font-size:11px; color:#7dd3fc; font-family:'Space Mono',monospace; margin:2px 0 0; }
.cel-badge {
    display:flex; align-items:center; gap:7px; font-size:11px;
    color:#00d4b4; font-family:'Space Mono',monospace; font-weight:700;
    background:rgba(0,212,180,0.1); border:1px solid rgba(0,212,180,0.3);
    border-radius:20px; padding:5px 14px;
}
.dot { width:7px; height:7px; background:#00d4b4; border-radius:50%;
       box-shadow:0 0 7px #00d4b4; display:inline-block; animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* ── left panel box ── */
.panel-box {
    background:#111627; border:1px solid #2a3a5c; border-radius:16px;
    padding:18px 14px; overflow-y:auto;
}
.panel-logo-icon {
    width:36px; height:36px; border-radius:10px;
    background:linear-gradient(135deg,#ff6d29,#ff9a56);
    display:flex; align-items:center; justify-content:center;
    font-size:18px; box-shadow:0 0 14px rgba(255,109,41,0.4);
}

/* ── welcome box ── */
.welcome-box {
    text-align:center; padding:48px 20px;
    background:linear-gradient(135deg,#141b2d,#1a2340);
    border:1px solid #2a3a5c; border-radius:18px; margin:0 0 16px;
}
.wel-title { font-size:22px; font-weight:700; color:#fff; margin-bottom:10px; }
.wel-title span { color:#ff6d29; }
.wel-sub { font-size:13.5px; color:#9ab0cc; max-width:500px; margin:0 auto; line-height:1.9; }
.wel-sub em { color:#7dd3fc; font-style:normal; font-weight:600; }

/* ── response badges ── */
.badge-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
.badge { border-radius:20px; padding:5px 14px; font-size:11px;
         font-family:'Space Mono',monospace; font-weight:700;
         display:inline-flex; align-items:center; gap:5px; }
.b-blue   { background:rgba(47,110,245,0.15); border:1px solid rgba(47,110,245,0.4);  color:#7dd3fc; }
.b-green  { background:rgba(0,212,180,0.12);  border:1px solid rgba(0,212,180,0.35);  color:#00d4b4; }
.b-orange { background:rgba(255,109,41,0.12); border:1px solid rgba(255,109,41,0.35); color:#ff9a56; }

/* ── misc ── */
.divider { height:1px; background:#2a3a5c; margin:14px 0; }
.sec-label {
    font-size:9px; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#7a8aab;
    font-family:'Space Mono',monospace; margin-bottom:8px;
}
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0b0e1a; }
::-webkit-scrollbar-thumb { background:#2a3a5c; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#2f6ef5; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  TOKEN COUNTER
# ══════════════════════════════════════════════════════════════════
def count_tokens(text: str) -> int:
    if not text: return 0
    if TIKTOKEN_OK: return len(_ENCODER.encode(text))
    return int(len(text.split()) * 1.3)

def record_tokens(p: int, r: int):
    st.session_state.token_stats["prompt"]   += p
    st.session_state.token_stats["response"] += r
    st.session_state.token_stats["total"]    += p + r
    st.session_state.token_stats["turns"]    += 1

def cost_estimate(tokens: int) -> str:
    c = (tokens / 1_000_000) * 0.59
    return f"~${c:.5f}" if c < 0.001 else f"~${c:.4f}"

# ══════════════════════════════════════════════════════════════════
#  RATE LIMITER
# ══════════════════════════════════════════════════════════════════
RATE_LIMITS = {
    "free":  {"requests": 10,  "window": 3600},
    "pro":   {"requests": 100, "window": 3600},
    "admin": {"requests": 999, "window": 3600},
}

def check_rate_limit() -> tuple[bool, str]:
    tier = st.session_state.rl_tier
    cfg  = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
    ts   = st.session_state.rl_timestamps
    cutoff = time.time() - cfg["window"]
    while ts and ts[0] < cutoff: ts.popleft()
    if len(ts) >= cfg["requests"]:
        retry = int(ts[0] + cfg["window"] - time.time()) + 1
        return False, (f"⏳ Rate limit reached ({cfg['requests']} req/hr on **{tier}** plan). "
                       f"Retry in **{retry//60}m {retry%60}s**.")
    ts.append(time.time())
    return True, ""

def rl_usage() -> dict:
    tier = st.session_state.rl_tier
    cfg  = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
    ts   = st.session_state.rl_timestamps
    cutoff = time.time() - cfg["window"]
    while ts and ts[0] < cutoff: ts.popleft()
    used = len(ts)
    return {"tier": tier, "used": used, "limit": cfg["requests"],
            "pct": int((used / cfg["requests"]) * 100)}

# ══════════════════════════════════════════════════════════════════
#  WEB SEARCH
# ══════════════════════════════════════════════════════════════════
def search_available() -> bool:
    return TAVILY_OK and bool(TAVILY_KEY)

def search_celonis(query: str, max_results: int = 4) -> list[dict]:
    if not search_available(): return []
    try:
        client = TavilyClient(api_key=TAVILY_KEY)
        resp   = client.search(
            query=f"Celonis {query}", search_depth="advanced",
            include_domains=["docs.celonis.com","community.celonis.com",
                             "celonis.com","academy.celonis.com"],
            max_results=max_results,
        )
        results = [{"title": r.get("title",""), "url": r.get("url",""),
                    "content": r.get("content","")[:800], "score": round(r.get("score",0),3)}
                   for r in resp.get("results",[])]
        _log("info", f"Search '{query}' → {len(results)} results")
        return results
    except Exception as e:
        _log("error", f"Tavily: {e}")
        return []

def format_search_ctx(results: list[dict]) -> str:
    if not results: return ""
    lines = ["### 🔍 Live Celonis Documentation\n"]
    for r in results:
        lines.append(f"**[{r['title']}]({r['url']})**\n{r['content']}\n")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════
#  MODELS & CONFIG
# ══════════════════════════════════════════════════════════════════
MODELS = {
    "⚡ Compound (Web Search)": "compound-beta",
    "🦙 Llama 3.3 70B":         "llama-3.3-70b-versatile",
    "🦙 Llama 4 Scout 17B":     "meta-llama/llama-4-scout-17b-16e-instruct",
    "🔮 Mixtral 8x7B":          "mixtral-8x7b-32768",
}
ANSWER_MODES = {
    "🎓 Guided (Beginner)":  "beginner",
    "⚡ Standard":            "standard",
    "🔬 Expert / Deep Dive": "expert",
    "📝 PQL Only":           "pql_only",
}
MODE_INSTRUCTIONS = {
    "beginner": "Use simple language, explain every term, use analogies, be encouraging. Add 'Plain English' summaries.",
    "standard": "Use ### headings, code blocks, **bold** key terms, 💡 Pro Tip, ⚠️ Common Pitfall, numbered steps.",
    "expert":   "Skip basics. Deep architecture, advanced PQL, performance, edge cases, enterprise trade-offs.",
    "pql_only": "Answer ONLY with PQL. Show complete snippets, explain each function, show alternatives, performance notes.",
}
SUGGESTIONS = [
    ("OLAP Views",       "How do I create an OLAP view in Celonis step by step?"),
    ("PQL Basics",       "What is PQL and how do I write a basic aggregation query?"),
    ("Process Explorer", "How does Process Explorer work in Celonis?"),
    ("Data Model",       "How do I create and configure a data model in Celonis?"),
    ("SAP Connector",    "How do I connect SAP ECC or S/4HANA data to Celonis?"),
    ("KPI Trees",        "How do I build KPI trees in Celonis Studio?"),
    ("Action Flows",     "How can I set up action flows and automations in Celonis?"),
    ("ML Workbench",     "What is the ML Workbench used for in Celonis?"),
    ("Permissions",      "How does role-based access and permissions work in Celonis?"),
]

def build_prompt(answer_mode: str, search_ctx: str = "") -> str:
    base = """You are an expert Celonis AI Assistant for the Celonis Process Intelligence platform.
Deep expertise in: Studio, OLAP Views, Process Explorer, Data Models, PQL (aggregations, CASE,
SOURCE(), TARGET(), REMAP_TIMESTAMPS()), Connectors (SAP ECC/S4HANA, Salesforce, ServiceNow),
ML Workbench, Permissions, Action Engine, KPI Trees.
Always search docs.celonis.com. Respond like a senior Celonis consultant — expert, practical, friendly."""
    mode_str   = MODE_INSTRUCTIONS.get(answer_mode, MODE_INSTRUCTIONS["standard"])
    search_str = f"\n\n### 🔍 Live Search Results\n{search_ctx}" if search_ctx else ""
    return f"{base}\n\n## Response Style\n{mode_str}{search_str}"

# ══════════════════════════════════════════════════════════════════
#  TOP BAR  (toggle button + header — always full width)
# ══════════════════════════════════════════════════════════════════
toggle_col, header_col = st.columns([0.4, 9.6], gap="small")

with toggle_col:
    icon = "✕" if st.session_state.panel_open else "☰"
    if st.button(icon, key="toggle_panel"):
        st.session_state.panel_open = not st.session_state.panel_open
        st.rerun()

with header_col:
    feat = []
    if search_available(): feat.append("🔍 Live Search")
    # model name filled after left panel renders — use placeholder for now
    feat_str = " · ".join(feat) if feat else "AI Knowledge"
    st.markdown(f"""
    <div class="cel-header">
      <div class="cel-header-left">
        <div style="font-size:26px;">⚡</div>
        <div>
          <p class="cel-title">Celonis AI Agent</p>
          <p class="cel-sub">{feat_str} · Powered by Groq</p>
        </div>
      </div>
      <div class="cel-badge"><span class="dot"></span> Live</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  MAIN LAYOUT  (panel width depends on toggle state)
# ══════════════════════════════════════════════════════════════════
if st.session_state.panel_open:
    left_col, right_col = st.columns([2.3, 7.7], gap="medium")
else:
    # Panel hidden — give full width to chat
    left_col, right_col = st.columns([0.01, 9.99], gap="small")

# ──────────────────────────────────────────────────
#  LEFT PANEL
# ──────────────────────────────────────────────────
with left_col:
    if st.session_state.panel_open:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
          <div class="panel-logo-icon">⚡</div>
          <div>
            <div style="font-size:15px;font-weight:700;color:#fff;">Celonis AI</div>
            <div style="font-size:10px;color:#7a8aab;font-family:Space Mono,monospace;">Powered by Groq</div>
          </div>
        </div>
        <div class="divider"></div>
        """, unsafe_allow_html=True)

        # Model selector
        st.markdown('<div class="sec-label">🤖 Model</div>', unsafe_allow_html=True)
        selected_label = st.selectbox("Model", list(MODELS.keys()), index=0,
                                      label_visibility="collapsed", key="model_select")
        selected_model = MODELS[selected_label]

        # Answer mode
        st.markdown('<div class="sec-label">🎯 Answer Mode</div>', unsafe_allow_html=True)
        mode_label  = st.selectbox("Mode", list(ANSWER_MODES.keys()), index=1,
                                   label_visibility="collapsed", key="mode_select")
        answer_mode = ANSWER_MODES[mode_label]

        # Status pills
        c1, c2 = st.columns(2)
        with c1:
            if search_available():
                st.success("🔍 Search ON", icon="✅")
            else:
                st.warning("🔍 No Search", icon="⚠️")
        with c2:
            st.success("🧮 Tiktoken" if TIKTOKEN_OK else "🧮 Approx",
                       icon="✅" if TIKTOKEN_OK else "ℹ️")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Quick questions
        st.markdown('<div class="sec-label">💬 Quick Questions</div>', unsafe_allow_html=True)
        for tag, question in SUGGESTIONS:
            if st.button(f"[{tag}]  {question}", key=f"q_{tag}"):
                st.session_state.prefill = question
                st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Stats
        st.markdown('<div class="sec-label">📊 Session Stats</div>', unsafe_allow_html=True)
        stats = st.session_state.token_stats
        usage = rl_usage()
        ca, cb = st.columns(2)
        with ca: st.metric("Tokens", f"{stats['total']:,}")
        with cb: st.metric("Cost",   cost_estimate(stats["total"]))

        pct      = usage["pct"]
        bar_icon = "🟢" if pct < 60 else ("🟡" if pct < 85 else "🔴")
        st.markdown(
            f'<div style="font-size:10px;color:#9ab0cc;margin-bottom:4px;">'
            f'{bar_icon} {usage["used"]}/{usage["limit"]} req/hr · {usage["tier"].upper()}</div>',
            unsafe_allow_html=True,
        )
        st.progress(min(pct / 100, 1.0))

        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_btn"):
            st.session_state.messages   = []
            st.session_state.token_stats = {"total":0,"prompt":0,"response":0,"turns":0}
            st.rerun()

        st.markdown(
            '<p style="font-size:9px;color:#7a8aab;text-align:center;'
            'font-family:Space Mono,monospace;margin-top:10px;">'
            'console.groq.com · app.tavily.com</p>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Panel is hidden — nothing rendered in this tiny column
        pass

# ──────────────────────────────────────────────────
#  RIGHT PANEL  — chat area
# ──────────────────────────────────────────────────
with right_col:

    # Read model/mode (with fallback when panel is closed)
    selected_model = st.session_state.get("model_select",  "compound-beta")
    selected_model = MODELS.get(selected_model, selected_model)
    answer_mode    = st.session_state.get("mode_select",   "standard")
    answer_mode    = ANSWER_MODES.get(answer_mode, answer_mode)

    # Welcome screen
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-box">
          <div style="font-size:50px;margin-bottom:16px;">⚡</div>
          <div class="wel-title">Ask anything about <span>Celonis</span></div>
          <div class="wel-sub">
            I combine live Celonis documentation search and expert AI to give you accurate,
            enhanced answers — step-by-step guides, PQL examples, and best practices.<br/><br/>
            <em>Try: "How do I create an OLAP view?" · "Explain PQL aggregations" · "Paste any PQL to explain"</em>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Chat history (messages scroll here) ──
    for msg in st.session_state.messages:
        avatar = "⚡" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ── Prefill from quick questions ──
    prefill = st.session_state.pop("prefill", None)

    # ── Chat input — Streamlit automatically pins this to bottom ──
    prompt = st.chat_input(
        "Ask about OLAP views, PQL, data models, SAP connectors, or paste PQL to explain…",
        key="chat_input",
    ) or prefill

    # ══════════════════════════════════════════════════════════════
    #  HANDLE PROMPT
    # ══════════════════════════════════════════════════════════════
    if prompt:
        if not GROQ_KEY:
            st.error("⚠️ No Groq API key found. Add `GROQ_API_KEY` to your Streamlit Cloud secrets.")
            st.stop()

        allowed, rl_msg = check_rate_limit()
        if not allowed:
            st.warning(rl_msg)
            st.stop()

        # User bubble
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # History (last 20)
        history = [{"role": m["role"], "content": m["content"]}
                   for m in st.session_state.messages[-20:]]

        # AI response
        with st.chat_message("assistant", avatar="⚡"):
            t0 = time.time()

            # Web search
            search_results, search_ctx = [], ""
            if search_available():
                with st.spinner("🔍 Searching Celonis docs…"):
                    search_results = search_celonis(prompt)
                    search_ctx     = format_search_ctx(search_results)

            system_prompt = build_prompt(answer_mode, search_ctx)
            p_tokens      = count_tokens(system_prompt) + count_tokens(prompt)

            try:
                client = Groq(api_key=GROQ_KEY)
                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role":"system","content":system_prompt}] + history,
                    max_completion_tokens=1500,
                    temperature=0.6,
                    stream=True,
                )

                full_response, placeholder = "", st.empty()
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

                r_tokens = count_tokens(full_response)
                record_tokens(p_tokens, r_tokens)
                latency  = (time.time() - t0) * 1000
                _log("info", f"QUERY model={selected_model} tokens={p_tokens+r_tokens} "
                             f"latency={latency:.0f}ms q={prompt[:60]!r}")

                # Badges
                badges = '<div class="badge-row">'
                if search_results:
                    badges += f'<span class="badge b-blue">🔍 {len(search_results)} docs</span>'
                badges += f'<span class="badge b-orange">⚡ {selected_model}</span>'
                badges += f'<span class="badge b-green">⏱ {latency/1000:.1f}s · {r_tokens} tok</span>'
                badges += '</div>'
                st.markdown(badges, unsafe_allow_html=True)

                if search_results:
                    with st.expander("📎 Sources", expanded=False):
                        for r in search_results:
                            st.markdown(f"- [{r['title']}]({r['url']}) `{r['score']}`")

                st.session_state.messages.append({"role":"assistant","content":full_response})

            except groq_errors.AuthenticationError:
                st.error("❌ Invalid Groq API Key in secrets.")
            except groq_errors.RateLimitError:
                st.error("⏳ Groq rate limit hit — wait a moment and retry.")
            except groq_errors.APIConnectionError as e:
                st.error(f"🌐 Connection error: {e}")
            except groq_errors.APIStatusError as e:
                st.error(f"⚠️ API error {e.status_code}: {e.message}")
            except Exception as e:
                _log("error", f"Unexpected: {e}")
                st.error(f"⚠️ Unexpected error: {e}")
