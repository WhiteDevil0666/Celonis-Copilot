import streamlit as st
from groq import Groq
import groq as groq_errors

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Celonis AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

/* ═══════════════════════════════════════════
   BASE — force dark theme everywhere
═══════════════════════════════════════════ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .main > div,
section.main,
[class*="css"] {
    background-color: #0b0e1a !important;
    color: #e8ecf4 !important;
    font-family: 'Sora', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding-top: 1.5rem !important;
    max-width: 100% !important;
    background-color: #0b0e1a !important;
}

/* All text everywhere */
p, span, li, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p, .stMarkdown span,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] ol,
[data-testid="stMarkdownContainer"] ul {
    color: #e8ecf4 !important;
}

/* ═══════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] section {
    background-color: #111627 !important;
    border-right: 1px solid #2a3a5c !important;
}

/* All text inside sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #c8d4e8 !important;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Sidebar quick-question buttons */
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid #2a3a5c !important;
    border-left: 3px solid transparent !important;
    text-align: left !important;
    color: #c8d4e8 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 12.5px !important;
    padding: 10px 12px !important;
    width: 100% !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
    white-space: normal !important;
    height: auto !important;
    line-height: 1.5 !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(47,110,245,0.15) !important;
    color: #ffffff !important;
    border-left-color: #2f6ef5 !important;
    border-color: #2f6ef5 !important;
}

/* Sidebar text inputs */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background-color: #1a2340 !important;
    color: #e8ecf4 !important;
    border: 1px solid #2a3a5c !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] input::placeholder {
    color: #7a8aab !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] [data-testid="stSelectbox"] div,
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] span {
    background-color: #1a2340 !important;
    color: #e8ecf4 !important;
    border-color: #2a3a5c !important;
}

/* Sidebar selectbox dropdown list */
[data-baseweb="popover"] ul,
[data-baseweb="menu"] ul,
[data-baseweb="popover"] li,
[data-baseweb="menu"] li {
    background-color: #1a2340 !important;
    color: #e8ecf4 !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover {
    background-color: #2a3a5c !important;
}

/* Sidebar metric */
[data-testid="stSidebar"] [data-testid="stMetric"] label,
[data-testid="stSidebar"] [data-testid="stMetric"] div {
    color: #c8d4e8 !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #00d4b4 !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: #2a3a5c !important;
    opacity: 1 !important;
}

/* Sidebar success/info alerts */
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] [data-testid="stNotification"] {
    background-color: #1a2340 !important;
    color: #e8ecf4 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stAlert p,
[data-testid="stSidebar"] [data-testid="stNotification"] p {
    color: #e8ecf4 !important;
}

/* ═══════════════════════════════════════════
   CHAT MESSAGES
═══════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background-color: #141b2d !important;
    border: 1px solid #2a3a5c !important;
    border-radius: 14px !important;
    margin-bottom: 12px !important;
    padding: 14px 18px !important;
}

/* Text inside chat bubbles */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
    color: #e8ecf4 !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
}

/* Headings inside chat */
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: #7dd3fc !important;
    font-weight: 700 !important;
    margin-top: 16px !important;
}

/* Bold inside chat */
[data-testid="stChatMessage"] strong {
    color: #c8d8ff !important;
}

/* Code inline */
[data-testid="stChatMessage"] code {
    background-color: #1e2d4a !important;
    color: #00d4b4 !important;
    padding: 2px 7px !important;
    border-radius: 5px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12.5px !important;
}

/* Code block */
[data-testid="stChatMessage"] pre {
    background-color: #0d1525 !important;
    border: 1px solid #2a3a5c !important;
    border-radius: 10px !important;
    padding: 16px !important;
    overflow-x: auto !important;
}
[data-testid="stChatMessage"] pre code {
    background: none !important;
    color: #a5d6ff !important;
    padding: 0 !important;
    font-size: 13px !important;
}

/* ═══════════════════════════════════════════
   CHAT INPUT BAR
═══════════════════════════════════════════ */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {
    background-color: #141b2d !important;
    border: 1px solid #2a3a5c !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background-color: #141b2d !important;
    color: #e8ecf4 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 14px !important;
    caret-color: #2f6ef5 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #7a8aab !important;
}
[data-testid="stChatInputSubmitButton"] svg {
    fill: #ffffff !important;
}

/* ═══════════════════════════════════════════
   MAIN AREA BUTTONS (Clear Chat, etc.)
═══════════════════════════════════════════ */
.main .stButton button,
[data-testid="stAppViewContainer"] .stButton button {
    background-color: #1a2340 !important;
    color: #e8ecf4 !important;
    border: 1px solid #2a3a5c !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
}
.main .stButton button:hover,
[data-testid="stAppViewContainer"] .stButton button:hover {
    background-color: #2f6ef5 !important;
    border-color: #2f6ef5 !important;
    color: #ffffff !important;
}

/* ═══════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════ */
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span {
    color: #7dd3fc !important;
}

/* ═══════════════════════════════════════════
   ERROR / WARNING ALERTS (main area)
═══════════════════════════════════════════ */
.stAlert { border-radius: 10px !important; }
[data-testid="stNotification"] p,
.stAlert p { color: #e8ecf4 !important; }

/* ═══════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0b0e1a; }
::-webkit-scrollbar-thumb { background: #2a3a5c; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2f6ef5; }

/* ═══════════════════════════════════════════
   CUSTOM HTML COMPONENTS
═══════════════════════════════════════════ */

/* Page header bar */
.celonis-header {
    background: linear-gradient(135deg, #141b2d 0%, #1a2340 100%);
    border: 1px solid #2a3a5c;
    border-radius: 14px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon { font-size: 32px; }
.header-title { font-size: 20px; font-weight: 700; margin: 0; color: #ffffff; }
.header-sub { font-size: 11px; color: #7dd3fc; font-family: 'Space Mono', monospace; margin: 2px 0 0; }
.status-live {
    display: flex; align-items: center; gap: 7px;
    font-size: 11px; color: #00d4b4;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
}
.dot-live {
    width: 8px; height: 8px; background: #00d4b4;
    border-radius: 50%; display: inline-block;
    box-shadow: 0 0 8px #00d4b4;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 8px #00d4b4;} 50%{opacity:0.4;box-shadow:none;} }

/* Welcome box */
.welcome-box {
    text-align: center;
    padding: 55px 20px;
    background: linear-gradient(135deg, #141b2d, #1a2340);
    border: 1px solid #2a3a5c;
    border-radius: 18px;
    margin: 20px 0;
}
.welcome-orb { font-size: 54px; margin-bottom: 18px; display: block; }
.welcome-title { font-size: 24px; font-weight: 700; margin-bottom: 12px; color: #ffffff !important; }
.welcome-title span { color: #ff6d29; }
.welcome-sub {
    font-size: 14px; color: #9ab0cc !important;
    max-width: 500px; margin: 0 auto;
    line-height: 1.9;
}
.welcome-sub em { color: #7dd3fc !important; font-style: normal; font-weight: 600; }

/* Badges */
.badge-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.source-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(47,110,245,0.15);
    border: 1px solid rgba(47,110,245,0.4);
    border-radius: 20px; padding: 5px 14px;
    font-size: 11px; color: #7dd3fc;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
}
.model-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,212,180,0.12);
    border: 1px solid rgba(0,212,180,0.35);
    border-radius: 20px; padding: 5px 14px;
    font-size: 11px; color: #00d4b4;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
}
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

Always be accurate to Celonis terminology. Key areas you know deeply:
- **Celonis Studio** — views, components, KPIs, action flows, apps
- **OLAP Views** — creating, configuring, PQL aggregations, dimensions, measures
- **Process Explorer** — variant analysis, conformance checking, happy path
- **Data Models** — tables, foreign keys, activity tables, event logs
- **PQL (Process Query Language)** — aggregations, filters, CASE statements, process functions like SOURCE(), TARGET(), REMAP_TIMESTAMPS()
- **Connectors & Data Pools** — SAP ECC, S/4HANA, Salesforce, ServiceNow, custom
- **ML Workbench** — machine learning, Python notebooks, predictions
- **Permissions** — team management, role-based access, packages
- **Action Engine** — automations, triggers, action flows
- **Business Questions & KPI Trees** — building insights

For OLAP views specifically: explain what they are, how to create one step-by-step, configuring dimensions and measures with PQL, filtering, performance tips, and how they differ from Process Explorer.

Always search docs.celonis.com for the most current and accurate information before answering.
Respond like a senior Celonis consultant — expert, practical, and friendly."""

# ── Available Groq Models ─────────────────────────────────────────────────────
MODELS = {
    "⚡ Compound (Web Search Built-in)": "groq/compound",
    "🦙 Llama 3.3 70B Versatile":        "llama-3.3-70b-versatile",
    "🦙 Llama 4 Scout 17B":              "meta-llama/llama-4-scout-17b-16e-instruct",
    "🔮 Mixtral 8x7B":                   "mixtral-8x7b-32768",
}

# ── Session State ─────────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "prefill"      not in st.session_state: st.session_state.prefill      = None
if "total_tokens" not in st.session_state: st.session_state.total_tokens = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Celonis AI Agent")
    st.markdown(
        '<p style="font-size:11px;color:#7a8aab;font-family:Space Mono,monospace;">'
        'Powered by Groq · docs.celonis.com</p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # API Key
    st.markdown("**🔑 Groq API Key**")
    groq_key_input = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your free key at console.groq.com",
        label_visibility="collapsed",
    )

    # Model selector
    st.markdown("**🤖 Model**")
    selected_model_label = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        index=0,
        label_visibility="collapsed",
        help="'Compound' has built-in web search for live Celonis docs. Other models use knowledge only.",
    )
    selected_model = MODELS[selected_model_label]

    is_compound = selected_model == "groq/compound"
    if is_compound:
        st.success("🔍 Live web search enabled", icon="✅")
    else:
        st.info("ℹ️ Using model knowledge only (no live search)", icon="💡")

    st.markdown("---")

    # Quick questions
    st.markdown(
        '<p style="font-size:10px;color:#7a8aab;text-transform:uppercase;'
        'letter-spacing:0.1em;font-family:Space Mono,monospace;">Quick Questions</p>',
        unsafe_allow_html=True,
    )

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

    for tag, question in SUGGESTIONS:
        if st.button(f"[{tag}] {question}", key=f"btn_{tag}"):
            st.session_state.prefill = question

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages     = []
            st.session_state.total_tokens = 0
            st.rerun()
    with col2:
        st.metric("Tokens", f"{st.session_state.total_tokens:,}")

    st.markdown(
        '<p style="font-size:10px;color:#7a8aab;text-align:center;'
        'font-family:Space Mono,monospace;margin-top:8px;">console.groq.com</p>',
        unsafe_allow_html=True,
    )

# ── Resolve API key ───────────────────────────────────────────────────────────
api_key = groq_key_input or st.secrets.get("GROQ_API_KEY", None)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="celonis-header">
  <div class="header-left">
    <div class="header-icon">⚡</div>
    <div>
      <p class="header-title">Celonis AI Agent</p>
      <p class="header-sub">Ask anything · {'Live web search via Groq Compound' if is_compound else 'AI knowledge · ' + selected_model_label}</p>
    </div>
  </div>
  <div class="status-live"><span class="dot-live"></span> Live</div>
</div>
""", unsafe_allow_html=True)

# ── Welcome screen ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
      <div class="welcome-orb">⚡</div>
      <div class="welcome-title">Ask anything about <span>Celonis</span></div>
      <div class="welcome-sub">
        I fetch real-time information from official Celonis documentation
        and enhance it with expert AI-powered explanations, step-by-step guides,
        PQL examples, and best practices.<br/><br/>
        <em>Try: "How do I create an OLAP view?" or "Explain PQL aggregation functions"</em>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Handle sidebar prefill ────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", None)

# ── Chat Input ────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask about OLAP views, PQL, data models, SAP connectors…") or prefill

if prompt:
    # Validate API key
    if not api_key:
        st.error("⚠️ Please enter your **Groq API Key** in the sidebar to continue. Get a free key at [console.groq.com](https://console.groq.com).")
        st.stop()

    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build message history (last 20 turns)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-20:]
    ]

    # ── Call Groq API ─────────────────────────────────────────────────────────
    with st.chat_message("assistant", avatar="⚡"):
        spinner_text = "🔍 Searching Celonis docs via Groq…" if is_compound else "🤖 Thinking…"

        with st.spinner(spinner_text):
            try:
                client = Groq(api_key=api_key)

                # Build kwargs — compound model supports built-in web search automatically
                kwargs = dict(
                    model=selected_model,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                    max_completion_tokens=1500,
                    temperature=0.6,
                    stream=True,
                )

                # Stream response
                stream = client.chat.completions.create(**kwargs)

                full_response = ""
                placeholder = st.empty()

                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    full_response += delta
                    placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

                # Track tokens (available on last chunk via x_groq or usage)
                try:
                    # For non-streaming: chunk.usage.total_tokens
                    # Estimate for streaming: rough word count × 1.3
                    estimated = int(len(full_response.split()) * 1.3)
                    st.session_state.total_tokens += estimated
                except Exception:
                    pass

                # Show source badge
                badge_html = '<div class="badge-row">'
                if is_compound:
                    badge_html += '<span class="source-badge">📎 docs.celonis.com · Live Search</span>'
                badge_html += f'<span class="model-badge">⚡ {selected_model}</span>'
                badge_html += '</div>'
                st.markdown(badge_html, unsafe_allow_html=True)

                # Save to history
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": full_response,
                })

            except groq_errors.AuthenticationError:
                st.error("❌ **Invalid API Key.** Please check your Groq API key in the sidebar.")
            except groq_errors.RateLimitError:
                st.error("⏳ **Rate limit reached.** Please wait a moment and try again.")
            except groq_errors.APIConnectionError as e:
                st.error(f"🌐 **Connection error:** {str(e)}")
            except groq_errors.APIStatusError as e:
                st.error(f"⚠️ **API error {e.status_code}:** {e.message}")
            except Exception as e:
                st.error(f"⚠️ **Unexpected error:** {str(e)}")
