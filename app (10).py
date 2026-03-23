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

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
    background-color: #0b0e1a !important;
    color: #e8ecf4 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111627 !important;
    border-right: 1px solid #1f2d4a !important;
}
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid transparent !important;
    text-align: left !important;
    color: #7a8aab !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 12.5px !important;
    padding: 10px 12px !important;
    width: 100% !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
    white-space: normal !important;
    height: auto !important;
    line-height: 1.5 !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #171e30 !important;
    color: #e8ecf4 !important;
    border-left-color: #2f6ef5 !important;
}

/* Chat messages */
.stChatMessage {
    background-color: #111627 !important;
    border: 1px solid #1f2d4a !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background-color: #111627 !important;
    color: #e8ecf4 !important;
    font-family: 'Sora', sans-serif !important;
    border: 1px solid #1f2d4a !important;
    border-radius: 12px !important;
}

/* Header */
.celonis-header {
    background: linear-gradient(135deg, #111627 0%, #171e30 100%);
    border: 1px solid #1f2d4a;
    border-radius: 14px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon { font-size: 32px; }
.header-title { font-size: 20px; font-weight: 700; margin: 0; color: #e8ecf4; }
.header-sub { font-size: 11px; color: #7a8aab; font-family: 'Space Mono', monospace; margin: 0; }
.status-live {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; color: #00d4b4;
    font-family: 'Space Mono', monospace;
}
.dot-live {
    width: 8px; height: 8px; background: #00d4b4;
    border-radius: 50%; display: inline-block;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Welcome */
.welcome-box {
    text-align: center; padding: 50px 20px;
    background: linear-gradient(135deg, #111627, #171e30);
    border: 1px solid #1f2d4a; border-radius: 16px; margin: 20px 0;
}
.welcome-orb { font-size: 52px; margin-bottom: 16px; }
.welcome-title { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
.welcome-title span { color: #ff6d29; }
.welcome-sub { font-size: 13.5px; color: #7a8aab; max-width: 480px; margin: 0 auto; line-height: 1.8; }

/* Source / model badge */
.badge-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.source-badge {
    display: inline-block;
    background: rgba(47,110,245,0.12);
    border: 1px solid rgba(47,110,245,0.3);
    border-radius: 20px; padding: 4px 12px;
    font-size: 10.5px; color: #2f6ef5;
    font-family: 'Space Mono', monospace;
}
.model-badge {
    display: inline-block;
    background: rgba(0,212,180,0.1);
    border: 1px solid rgba(0,212,180,0.3);
    border-radius: 20px; padding: 4px 12px;
    font-size: 10.5px; color: #00d4b4;
    font-family: 'Space Mono', monospace;
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
