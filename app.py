"""
app.py  —  Celonis AI Agent SaaS
========================================
Production-grade Streamlit app with:
  ✅ Real web search  (Tavily)
  ✅ RAG              (FAISS + Celonis docs)
  ✅ Rate limiting    (sliding window, per tier)
  ✅ Accurate tokens  (tiktoken)
  ✅ Structured logs  (loguru)
  ✅ Auth             (Supabase / API-key fallback)
  ✅ Answer modes     (Beginner / Standard / Expert / PQL)
  ✅ Always-visible panel (st.columns, no sidebar collapse)

Run:
  streamlit run app.py

First-time RAG setup:
  python -m rag.ingest
"""

import time
import streamlit as st
from groq import Groq
import groq as groq_errors

# ── Internal modules ──────────────────────────────────────────────────────────
from components.styles       import inject_css
from components.left_panel   import render_left_panel
from utils.auth              import render_auth_form, is_logged_in, get_current_user
from utils.rate_limiter      import get_rate_limiter
from utils.token_counter     import count_tokens, record_tokens, get_token_stats, init_token_tracker
from utils.web_search        import search_celonis_docs, format_search_context, is_search_available
from utils.prompts           import build_system_prompt
from utils.logger            import logger, log_query, log_error
from rag.retriever           import retrieve_context, is_rag_available

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Celonis AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
inject_css()
init_token_tracker()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.markdown("""
    <div style="max-width:480px;margin:60px auto;text-align:center;">
      <div style="font-size:50px;margin-bottom:16px;">⚡</div>
      <h2 style="color:#fff;font-size:24px;margin-bottom:8px;">Celonis AI Agent</h2>
      <p style="color:#9ab0cc;font-size:14px;margin-bottom:28px;">
        Your AI-powered guide to the Celonis platform.<br/>
        Sign in to start asking questions.
      </p>
    </div>
    """, unsafe_allow_html=True)

    auth_col = st.columns([1, 2, 1])[1]
    with auth_col:
        authenticated = render_auth_form()

    if not authenticated:
        st.stop()

# ── Session state defaults ────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "prefill"  not in st.session_state: st.session_state.prefill  = None

user    = get_current_user()
user_id = user["id"] if user else "anon"

# ── Two-column layout ─────────────────────────────────────────────────────────
left_col, right_col = st.columns([2.2, 7.8], gap="medium")

# ══════════════════════════════════════════════
#  LEFT PANEL
# ══════════════════════════════════════════════
with left_col:
    cfg = render_left_panel()

groq_key      = cfg["groq_key"]
selected_model = cfg["selected_model"]
is_compound   = cfg["is_compound"]
answer_mode   = cfg["answer_mode"]

# ══════════════════════════════════════════════
#  RIGHT PANEL
# ══════════════════════════════════════════════
with right_col:

    # Header bar
    search_on = is_search_available()
    rag_on    = is_rag_available()

    features = []
    if search_on: features.append("🔍 Live Search")
    if rag_on:    features.append("📚 RAG")
    feature_str = " · ".join(features) if features else f"Model: {selected_model}"

    st.markdown(f"""
    <div class="celonis-header">
      <div class="header-left">
        <div class="header-icon">⚡</div>
        <div>
          <p class="header-title">Celonis AI Agent</p>
          <p class="header-sub">{feature_str} · {answer_mode.replace("_"," ").title()} mode</p>
        </div>
      </div>
      <div class="status-badge"><span class="dot-live"></span> Live</div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome screen
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-box">
          <div style="font-size:50px;margin-bottom:16px;">⚡</div>
          <div class="welcome-title">Ask anything about <span>Celonis</span></div>
          <div class="welcome-sub">
            I combine live Celonis documentation search, embedded knowledge base,
            and expert AI to give you the most accurate, enhanced answers possible.<br/><br/>
            <em>Try: "How do I create an OLAP view?" · "Explain PQL aggregations" · "Explain this PQL: COUNT(CASE WHEN ...)"</em>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.messages:
        avatar = "⚡" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Handle sidebar prefill
    prefill = st.session_state.pop("prefill", None)

    # Chat input
    prompt = st.chat_input(
        "Ask about OLAP views, PQL, data models, SAP connectors, or paste a PQL to explain…",
        key="chat_input",
    ) or prefill

    if prompt:
        # ── API key check ─────────────────────────────────────────────────────
        if not groq_key:
            st.error("⚠️ Enter your **Groq API Key** in the left panel. Free key at [console.groq.com](https://console.groq.com).")
            st.stop()

        # ── Rate limit check ──────────────────────────────────────────────────
        rl = get_rate_limiter()
        allowed, rl_msg, remaining = rl.check(user_id)
        if not allowed:
            st.warning(rl_msg)
            st.stop()

        # ── Show user message ─────────────────────────────────────────────────
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # ── Build history (last 20 turns) ─────────────────────────────────────
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-20:]
        ]

        # ── AI response ───────────────────────────────────────────────────────
        with st.chat_message("assistant", avatar="⚡"):
            t_start = time.time()

            with st.spinner("⚡ Thinking…"):

                # 1. RAG retrieval
                rag_context_text = ""
                rag_sources      = []
                if rag_on:
                    rag_context_text, rag_sources = retrieve_context(prompt)

                # 2. Web search
                search_context_text = ""
                search_results      = []
                if search_on:
                    search_results      = search_celonis_docs(prompt)
                    search_context_text = format_search_context(search_results)

                # 3. Build system prompt with context injected
                system_prompt = build_system_prompt(
                    answer_mode    = answer_mode,
                    rag_context    = rag_context_text,
                    search_context = search_context_text,
                )

                # 4. Count prompt tokens accurately
                prompt_token_count = count_tokens(system_prompt) + count_tokens(prompt)

            try:
                client = Groq(api_key=groq_key)

                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": "system", "content": system_prompt}] + history,
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

                # 5. Accurate token count for response
                response_token_count = count_tokens(full_response)
                record_tokens(prompt_token_count, response_token_count)

                # 6. Latency
                latency_ms = (time.time() - t_start) * 1000

                # 7. Structured log
                log_query(
                    user_id   = user_id,
                    query     = prompt,
                    model     = selected_model,
                    tokens    = prompt_token_count + response_token_count,
                    latency_ms= latency_ms,
                )

                # 8. Source badges
                badges = '<div class="badge-row">'
                if search_on and search_results:
                    badges += f'<span class="badge badge-blue">🔍 {len(search_results)} Celonis docs</span>'
                if rag_on and rag_sources:
                    badges += f'<span class="badge badge-green">📚 {len(rag_sources)} RAG chunks</span>'
                badges += f'<span class="badge badge-orange">⚡ {selected_model}</span>'
                badges += f'<span class="badge badge-blue">⏱ {latency_ms/1000:.1f}s · {response_token_count} tokens</span>'
                badges += '</div>'
                st.markdown(badges, unsafe_allow_html=True)

                # 9. Show sources expander
                if rag_sources or search_results:
                    with st.expander("📎 View Sources", expanded=False):
                        if search_results:
                            st.markdown("**🔍 Web Search Sources**")
                            for r in search_results:
                                st.markdown(f"- [{r['title']}]({r['url']}) `score: {r['score']}`")
                        if rag_sources:
                            st.markdown("**📚 Knowledge Base Chunks**")
                            for i, s in enumerate(rag_sources, 1):
                                st.markdown(f"- **Chunk {i}** from `{s['url']}` `score: {s['score']}`")

                # 10. Save to history
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": full_response,
                })

            except groq_errors.AuthenticationError:
                log_error(user_id, Exception("AuthenticationError"), "chat")
                st.error("❌ **Invalid Groq API Key.** Check the left panel.")
            except groq_errors.RateLimitError:
                log_error(user_id, Exception("RateLimitError"), "chat")
                st.error("⏳ **Groq rate limit hit.** Wait a moment and retry.")
            except groq_errors.APIConnectionError as e:
                log_error(user_id, e, "chat")
                st.error(f"🌐 **Connection error:** {e}")
            except groq_errors.APIStatusError as e:
                log_error(user_id, e, "chat")
                st.error(f"⚠️ **API error {e.status_code}:** {e.message}")
            except Exception as e:
                log_error(user_id, e, "chat")
                st.error(f"⚠️ **Unexpected error:** {e}")
                logger.exception(f"Unhandled exception for user {user_id}")
