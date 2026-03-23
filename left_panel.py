"""
components/left_panel.py
Renders the always-visible left panel (replaces native Streamlit sidebar).
"""

import streamlit as st
from utils.rate_limiter import get_rate_limiter
from utils.token_counter import get_token_stats
from utils.web_search import is_search_available
from rag.retriever import is_rag_available
from utils.auth import is_logged_in, get_current_user, get_user_tier, sign_out


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


def render_left_panel() -> dict:
    """
    Renders the left panel and returns config dict:
    {groq_key, tavily_key, selected_model, is_compound, answer_mode}
    """

    # ── Logo ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
      <div style="width:36px;height:36px;border-radius:10px;
                  background:linear-gradient(135deg,#ff6d29,#ff9a56);
                  display:flex;align-items:center;justify-content:center;
                  font-size:18px;box-shadow:0 0 14px rgba(255,109,41,0.4);">⚡</div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#fff;">Celonis AI</div>
        <div style="font-size:10px;color:#7a8aab;font-family:Space Mono,monospace;">Powered by Groq</div>
      </div>
    </div>
    <div class="panel-divider"></div>
    """, unsafe_allow_html=True)

    # ── User info / tier ──────────────────────────────────────────────────────
    if is_logged_in():
        user = get_current_user()
        tier = get_user_tier()
        tier_color = {"free": "#7a8aab", "pro": "#00d4b4", "admin": "#ff6d29"}.get(tier, "#7a8aab")
        st.markdown(
            f'<div style="font-size:11px;color:{tier_color};font-family:Space Mono,monospace;'
            f'margin-bottom:6px;">👤 {user["email"]} &nbsp;|&nbsp; '
            f'<b style="color:{tier_color};">{tier.upper()}</b></div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", key="signout_btn"):
            sign_out()
            st.rerun()
        st.markdown('<div class="panel-divider"></div>', unsafe_allow_html=True)

    # ── API Keys ──────────────────────────────────────────────────────────────
    st.markdown('<div class="panel-section-label">🔑 API Keys</div>', unsafe_allow_html=True)

    groq_key = st.text_input(
        "Groq Key", type="password", placeholder="gsk_...",
        help="Free at console.groq.com", label_visibility="collapsed",
        key="groq_key_input",
    ) or st.secrets.get("GROQ_API_KEY", "")

    tavily_key = st.text_input(
        "Tavily Key (Web Search)", type="password", placeholder="tvly-...",
        help="Free at app.tavily.com — enables real Celonis doc search",
        label_visibility="collapsed", key="tavily_key_input",
    ) or st.secrets.get("TAVILY_API_KEY", "")

    # Store tavily key in session for web_search module
    if tavily_key:
        st.session_state.tavily_key = tavily_key

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Model ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="panel-section-label">🤖 Model</div>', unsafe_allow_html=True)
    selected_label = st.selectbox(
        "Model", options=list(MODELS.keys()), index=0,
        label_visibility="collapsed", key="model_select",
    )
    selected_model = MODELS[selected_label]
    is_compound    = "compound" in selected_model

    # ── Answer Mode ───────────────────────────────────────────────────────────
    st.markdown('<div class="panel-section-label">🎯 Answer Mode</div>', unsafe_allow_html=True)
    mode_label   = st.selectbox(
        "Mode", options=list(ANSWER_MODES.keys()), index=1,
        label_visibility="collapsed", key="mode_select",
    )
    answer_mode = ANSWER_MODES[mode_label]

    # ── Status indicators ─────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        if is_search_available():
            st.success("🔍 Search ON", icon="✅")
        else:
            st.warning("🔍 Search OFF", icon="⚠️")
    with col_b:
        if is_rag_available():
            st.success("📚 RAG ON", icon="✅")
        else:
            st.warning("📚 RAG OFF", icon="⚠️")

    st.markdown('<div class="panel-divider"></div>', unsafe_allow_html=True)

    # ── Quick Questions ───────────────────────────────────────────────────────
    st.markdown('<div class="panel-section-label">💬 Quick Questions</div>', unsafe_allow_html=True)
    for tag, question in SUGGESTIONS:
        if st.button(f"[{tag}]  {question}", key=f"q_{tag}"):
            st.session_state.prefill = question
            st.rerun()

    st.markdown('<div class="panel-divider"></div>', unsafe_allow_html=True)

    # ── Usage stats ───────────────────────────────────────────────────────────
    st.markdown('<div class="panel-section-label">📊 Session Stats</div>', unsafe_allow_html=True)

    token_stats = get_token_stats()
    rl          = get_rate_limiter()
    rl_usage    = rl.get_usage()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Tokens", f"{token_stats['session_total']:,}")
    with c2:
        st.metric("Cost", token_stats["cost_estimate"])

    # Rate limit progress bar
    pct = rl_usage["pct"]
    bar_color = "🟢" if pct < 60 else ("🟡" if pct < 85 else "🔴")
    st.markdown(
        f'<div style="font-size:10px;color:#9ab0cc;margin-bottom:4px;">'
        f'{bar_color} {rl_usage["used"]}/{rl_usage["limit"]} requests '
        f'({rl_usage["tier"].upper()} · {rl_usage["window_h"]}h window)</div>',
        unsafe_allow_html=True,
    )
    st.progress(min(pct / 100, 1.0))

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_btn"):
        st.session_state.messages     = []
        st.session_state.token_stats  = {}
        st.rerun()

    st.markdown(
        '<p style="font-size:9px;color:#7a8aab;text-align:center;'
        'font-family:Space Mono,monospace;margin-top:10px;">'
        'console.groq.com · app.tavily.com</p>',
        unsafe_allow_html=True,
    )

    return {
        "groq_key":      groq_key,
        "tavily_key":    tavily_key,
        "selected_model": selected_model,
        "is_compound":   is_compound,
        "answer_mode":   answer_mode,
    }
