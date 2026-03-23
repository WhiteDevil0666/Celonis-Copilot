import streamlit as st
from groq import Groq
import groq as groq_errors

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Celonis AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",   # collapse native sidebar — we build our own
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

/* ── RESET & BASE ── */
html, body { background:#0b0e1a !important; color:#e8ecf4 !important; }

[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
.main, section.main, .block-container {
    background:#0b0e1a !important;
    color:#e8ecf4 !important;
    font-family:'Sora',sans-serif !important;
    padding-top:0.8rem !important;
    max-width:100% !important;
}

/* Hide Streamlit chrome completely */
#MainMenu, footer, header,
[data-testid="stHeader"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNav"],
button[kind="header"] { display:none !important; visibility:hidden !important; }

/* Hide the native sidebar entirely */
[data-testid="stSidebar"] { display:none !important; }

/* ── ALL TEXT ── */
p, span, li, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, [data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color:#e8ecf4 !important; }

/* ── LEFT PANEL ── */
.left-panel {
    background:#111627;
    border:1px solid #2a3a5c;
    border-radius:16px;
    padding:20px 14px;
    height:calc(100vh - 80px);
    overflow-y:auto;
    position:sticky;
    top:10px;
}
.left-panel::-webkit-scrollbar { width:4px; }
.left-panel::-webkit-scrollbar-thumb { background:#2a3a5c; border-radius:4px; }

.panel-logo {
    display:flex; align-items:center; gap:10px;
    margin-bottom:4px;
}
.panel-logo-icon {
    width:36px; height:36px; border-radius:10px;
    background:linear-gradient(135deg,#ff6d29,#ff9a56);
    display:flex; align-items:center; justify-content:center;
    font-size:18px; flex-shrink:0;
    box-shadow:0 0 14px rgba(255,109,41,0.4);
}
.panel-title { font-size:15px; font-weight:700; color:#fff; }
.panel-sub { font-size:10px; color:#7a8aab; font-family:'Space Mono',monospace; margin-top:2px; }

.panel-divider { height:1px; background:#2a3a5c; margin:14px 0; }

.panel-section-label {
    font-size:9px; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:#7a8aab;
    font-family:'Space Mono',monospace;
    margin-bottom:8px;
}

/* ── INPUT FIELDS ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    background:#1a2340 !important;
    color:#e8ecf4 !important;
    border:1px solid #2a3a5c !important;
    border-radius:8px !important;
    font-family:'Sora',sans-serif !important;
    font-size:13px !important;
}
[data-testid="stTextInput"] input::placeholder { color:#7a8aab !important; }
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label { color:#c8d4e8 !important; font-size:12px !important; }

/* Selectbox dropdown */
[data-baseweb="popover"] ul,
[data-baseweb="menu"] ul { background:#1a2340 !important; }
[data-baseweb="popover"] li,
[data-baseweb="menu"] li { color:#e8ecf4 !important; }
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover { background:#2a3a5c !important; }

/* ── ALL BUTTONS ── */
.stButton > button {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid #2a3a5c !important;
    color:#c8d4e8 !important;
    font-family:'Sora',sans-serif !important;
    font-size:12px !important;
    text-align:left !important;
    border-radius:8px !important;
    padding:9px 12px !important;
    width:100% !important;
    white-space:normal !important;
    height:auto !important;
    line-height:1.5 !important;
    margin-bottom:3px !important;
    transition:all 0.18s !important;
}
.stButton > button:hover {
    background:rgba(47,110,245,0.18) !important;
    border-color:#2f6ef5 !important;
    color:#fff !important;
}

/* Alert boxes */
.stAlert { border-radius:8px !important; background:#1a2340 !important; }
.stAlert p, [data-testid="stNotification"] p { color:#e8ecf4 !important; font-size:12px !important; }

/* Metric */
[data-testid="stMetric"] label { color:#9ab0cc !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#00d4b4 !important; font-size:18px !important; }

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background:#141b2d !important;
    border:1px solid #2a3a5c !important;
    border-radius:14px !important;
    padding:14px 18px !important;
    margin-bottom:10px !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
    color:#e8ecf4 !important;
    font-size:14px !important;
    line-height:1.8 !important;
}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
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
    background:none !important; color:#a5d6ff !important;
    padding:0 !important; font-size:13px !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] {
    background:#141b2d !important;
    border:1px solid #2a3a5c !important;
    border-radius:14px !important;
}
[data-testid="stChatInput"] textarea {
    background:#141b2d !important;
    color:#e8ecf4 !important;
    font-family:'Sora',sans-serif !important;
    font-size:14px !important;
    caret-color:#2f6ef5 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color:#7a8aab !important; }

/* ── HEADER BAR ── */
.celonis-header {
    background:linear-gradient(135deg,#141b2d,#1a2340);
    border:1px solid #2a3a5c;
    border-radius:14px;
    padding:14px 20px;
    margin-bottom:14px;
    display:flex; align-items:center; justify-content:space-between;
}
.header-left { display:flex; align-items:center; gap:12px; }
.header-icon { font-size:28px; }
.header-title { font-size:18px; font-weight:700; color:#fff; margin:0; }
.header-sub { font-size:11px; color:#7dd3fc; font-family:'Space Mono',monospace; margin:2px 0 0; }
.status-badge {
    display:flex; align-items:center; gap:7px;
    font-size:11px; color:#00d4b4;
    font-family:'Space Mono',monospace; font-weight:700;
    background:rgba(0,212,180,0.1); border:1px solid rgba(0,212,180,0.3);
    border-radius:20px; padding:5px 14px;
}
.dot-live {
    width:7px; height:7px; background:#00d4b4; border-radius:50%;
    box-shadow:0 0 7px #00d4b4; display:inline-block;
    animation:blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* ── WELCOME BOX ── */
.welcome-box {
    text-align:center; padding:48px 20px;
    background:linear-gradient(135deg,#141b2d,#1a2340);
    border:1px solid #2a3a5c; border-radius:18px; margin:10px 0 20px;
}
.welcome-orb { font-size:50px; margin-bottom:16px; display:block; }
.welcome-title { font-size:22px; font-weight:700; color:#fff; margin-bottom:10px; }
.welcome-title span { color:#ff6d29; }
.welcome-sub { font-size:13.5px; color:#9ab0cc; max-width:500px; margin:0 auto; line-height:1.9; }
.welcome-sub em { color:#7dd3fc; font-style:normal; font-weight:600; }

/* ── BADGES ── */
.badge-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
.source-badge {
    background:rgba(47,110,245,0.15); border:1px solid rgba(47,110,245,0.4);
    border-radius:20px; padding:5px 14px;
    font-size:11px; color:#7dd3fc;
    font-family:'Space Mono',monospace; font-weight:700;
}
.model-badge {
    background:rgba(0,212,180,0.12); border:1px solid rgba(0,212,180,0.35);
    border-radius:20px; padding:5px 14px;
    font-size:11px; color:#00d4b4;
    font-family:'Space Mono',monospace; font-weight:700;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0b0e1a; }
::-webkit-scrollbar-thumb { background:#2a3a5c; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#2f6ef5; }
</style>
""", unsafe_allow_html=True)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Celonis AI Assistant — a highly knowledgeable guide for the Celonis Process Intelligence platform.

Your role is to answer any user question about Celonis by:
1. Searching the web for the latest information from docs.celonis.com and official Celonis resources
2. Providing accurate, detailed information sourced from official Celonis documentation
3. ENHANCING the documentation with:
   - Clear step-by-step instructions (numbered, easy to follow)
   - Real-world use cases and practical examples
   - Pro tips and best practices not always in the docs
   - Common pitfalls and how to avoid them
   - PQL (Process Query Language) code examples where relevant

Format your answers with:
- Clear section headings using ###
- Code blocks for PQL, SQL, or config examples
- **Bold** for key Celonis terms on first use
- A "💡 Pro Tip" section when relevant
- A "⚠️ Common Pitfall" section when there's something users often get wrong
- Numbered steps for procedures

Always be accurate to Celonis terminology. Key areas:
- **Celonis Studio** — views, components, KPIs, action flows, apps
- **OLAP Views** — creating, configuring, PQL aggregations, dimensions, measures
- **Process Explorer** — variant analysis, conformance checking, happy path
- **Data Models** — tables, foreign keys, activity tables, event logs
- **PQL** — aggregations, filters, CASE, SOURCE(), TARGET(), REMAP_TIMESTAMPS()
- **Connectors & Data Pools** — SAP ECC, S/4HANA, Salesforce, ServiceNow, custom
- **ML Workbench** — machine learning, Python notebooks, predictions
- **Permissions** — team management, role-based access, packages
- **Action Engine** — automations, triggers, action flows

Always search docs.celonis.com for the most current and accurate information.
Respond like a senior Celonis consultant — expert, practical, and friendly."""

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = {
    "⚡ Compound (Web Search)": "compound-beta",
    "🦙 Llama 3.3 70B":         "llama-3.3-70b-versatile",
    "🦙 Llama 4 Scout 17B":     "meta-llama/llama-4-scout-17b-16e-instruct",
    "🔮 Mixtral 8x7B":          "mixtral-8x7b-32768",
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

# ── Session State ─────────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "prefill"      not in st.session_state: st.session_state.prefill      = None
if "total_tokens" not in st.session_state: st.session_state.total_tokens = 0

# ── Two-column layout (always visible, no collapsible sidebar) ────────────────
left_col, right_col = st.columns([2.2, 7.8], gap="medium")

# ═══════════════════════════════════════════════
#  LEFT PANEL
# ═══════════════════════════════════════════════
with left_col:
    st.markdown("""
    <div class="panel-logo">
      <div class="panel-logo-icon">⚡</div>
      <div>
        <div class="panel-title">Celonis AI</div>
        <div class="panel-sub">Powered by Groq</div>
      </div>
    </div>
    <div class="panel-divider"></div>
    """, unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="panel-section-label">🔑 Groq API Key</div>', unsafe_allow_html=True)
    groq_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="gsk_...",
        help="Free key at console.groq.com",
        label_visibility="collapsed",
        key="api_key_input",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Model selector
    st.markdown('<div class="panel-section-label">🤖 Model</div>', unsafe_allow_html=True)
    selected_label = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_model = MODELS[selected_label]
    is_compound    = "compound" in selected_model

    if is_compound:
        st.success("🔍 Live web search ON", icon="✅")
    else:
        st.info("Knowledge only — no live search", icon="💡")

    st.markdown('<div class="panel-divider"></div>', unsafe_allow_html=True)

    # Quick questions
    st.markdown('<div class="panel-section-label">💬 Quick Questions</div>', unsafe_allow_html=True)
    for tag, question in SUGGESTIONS:
        if st.button(f"[{tag}]  {question}", key=f"q_{tag}"):
            st.session_state.prefill = question
            st.rerun()

    st.markdown('<div class="panel-divider"></div>', unsafe_allow_html=True)

    # Footer controls
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_btn"):
            st.session_state.messages     = []
            st.session_state.total_tokens = 0
            st.rerun()
    with c2:
        st.metric("Tokens", f"{st.session_state.total_tokens:,}")

    st.markdown(
        '<p style="font-size:9px;color:#7a8aab;text-align:center;'
        'font-family:Space Mono,monospace;margin-top:10px;">console.groq.com</p>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════
#  RIGHT PANEL — header + chat
# ═══════════════════════════════════════════════
with right_col:

    api_key = groq_key_input or st.secrets.get("GROQ_API_KEY", "")

    # Header bar
    search_label = "Live web search via Groq Compound" if is_compound else f"Model: {selected_label}"
    st.markdown(f"""
    <div class="celonis-header">
      <div class="header-left">
        <div class="header-icon">⚡</div>
        <div>
          <p class="header-title">Celonis AI Agent</p>
          <p class="header-sub">{search_label}</p>
        </div>
      </div>
      <div class="status-badge"><span class="dot-live"></span> Live</div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome screen
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-box">
          <span class="welcome-orb">⚡</span>
          <div class="welcome-title">Ask anything about <span>Celonis</span></div>
          <div class="welcome-sub">
            I fetch real-time information from official Celonis documentation and
            enhance it with expert AI-powered explanations, step-by-step guides,
            PQL examples, and best practices.<br/><br/>
            <em>Try: "How do I create an OLAP view?" or "Explain PQL aggregation functions"</em>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.messages:
        avatar = "⚡" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Handle prefill
    prefill = st.session_state.pop("prefill", None)

    # Chat input
    prompt = st.chat_input(
        "Ask about OLAP views, PQL, data models, SAP connectors…",
        key="chat_input",
    ) or prefill

    if prompt:
        if not api_key:
            st.error("⚠️ Enter your **Groq API Key** in the left panel. Free key at [console.groq.com](https://console.groq.com).")
            st.stop()

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-20:]
        ]

        with st.chat_message("assistant", avatar="⚡"):
            spinner_msg = "🔍 Searching Celonis docs…" if is_compound else "🤖 Generating answer…"
            with st.spinner(spinner_msg):
                try:
                    client = Groq(api_key=api_key)

                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                        max_completion_tokens=1500,
                        temperature=0.6,
                        stream=True,
                    )

                    full_response = ""
                    placeholder   = st.empty()

                    for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        full_response += delta
                        placeholder.markdown(full_response + "▌")

                    placeholder.markdown(full_response)

                    st.session_state.total_tokens += int(len(full_response.split()) * 1.3)

                    badge = '<div class="badge-row">'
                    if is_compound:
                        badge += '<span class="source-badge">📎 docs.celonis.com · Live Search</span>'
                    badge += f'<span class="model-badge">⚡ {selected_model}</span></div>'
                    st.markdown(badge, unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role":    "assistant",
                        "content": full_response,
                    })

                except groq_errors.AuthenticationError:
                    st.error("❌ **Invalid API Key.** Check your Groq key in the left panel.")
                except groq_errors.RateLimitError:
                    st.error("⏳ **Rate limit hit.** Wait a moment then try again.")
                except groq_errors.APIConnectionError as e:
                    st.error(f"🌐 **Connection error:** {e}")
                except groq_errors.APIStatusError as e:
                    st.error(f"⚠️ **API error {e.status_code}:** {e.message}")
                except Exception as e:
                    st.error(f"⚠️ **Unexpected error:** {e}")
