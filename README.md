# ⚡ Celonis AI Agent — Full SaaS Architecture

Production-grade AI assistant for the Celonis Process Intelligence platform.

---

## 🏗️ Project Structure

```
celonis-ai-agent/
│
├── app.py                        ← Main entry point
├── requirements.txt
│
├── .streamlit/
│   ├── config.toml               ← Dark theme config
│   └── secrets.toml              ← API keys (never commit)
│
├── components/
│   ├── styles.py                 ← All CSS (single source of truth)
│   └── left_panel.py             ← Always-visible left panel
│
├── utils/
│   ├── auth.py                   ← Supabase auth + session management
│   ├── rate_limiter.py           ← Sliding window rate limiter (free/pro/admin)
│   ├── token_counter.py          ← Accurate tiktoken counting + cost estimates
│   ├── web_search.py             ← REAL web search via Tavily API
│   ├── prompts.py                ← Dynamic system prompt builder (4 modes)
│   └── logger.py                 ← Structured logging (loguru)
│
├── rag/
│   ├── ingest.py                 ← Scrape + embed Celonis docs → FAISS
│   └── retriever.py              ← RAG retrieval + context injection
│
└── logs/                         ← Auto-created by loguru
    ├── app_YYYY-MM-DD.log
    └── errors.log
```

---

## 🚀 Setup (Local)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your API keys
Edit `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY   = "gsk_..."      # Required — free at console.groq.com
TAVILY_API_KEY = "tvly_..."     # Recommended — free at app.tavily.com
SUPABASE_URL   = "https://..."  # Optional — for auth
SUPABASE_KEY   = "..."          # Optional — for auth
```

### 3. Build the RAG knowledge base (one-time)
```bash
python -m rag.ingest
```
This scrapes ~15 key Celonis documentation pages and builds a FAISS
vector index at `rag/vector_store/`. Takes ~2–3 minutes on first run.
Re-run whenever you want to update the knowledge base.

### 4. Run the app
```bash
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push to GitHub (add `logs/` and `rag/vector_store/` to `.gitignore`,
   OR commit the vector store so you don't need to rebuild on cold start)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set main file: `app.py`
4. Under **Advanced → Secrets**, paste your `secrets.toml` contents
5. Deploy ✅

**Note:** The RAG vector store must either be:
- Committed to the repo (simplest), OR
- Rebuilt on startup (add `rag.ingest.build_vector_store()` call to app.py)

---

## 🔑 API Keys — Where to Get Them

| Key | Where | Cost |
|-----|-------|------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Free tier available |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | 1,000 searches/month free |
| `SUPABASE_URL/KEY` | [supabase.com](https://supabase.com) | Free tier (500MB DB) |

---

## ✨ Features

| Feature | Implementation | File |
|---------|---------------|------|
| ✅ Real web search | Tavily API → docs.celonis.com | `utils/web_search.py` |
| ✅ RAG knowledge base | FAISS + sentence-transformers | `rag/` |
| ✅ Rate limiting | Sliding window (free/pro/admin) | `utils/rate_limiter.py` |
| ✅ Accurate token count | tiktoken (cl100k_base) | `utils/token_counter.py` |
| ✅ Cost estimation | $0.59/1M tokens (Groq pricing) | `utils/token_counter.py` |
| ✅ Structured logging | loguru (file + console) | `utils/logger.py` |
| ✅ Auth | Supabase / API-key fallback | `utils/auth.py` |
| ✅ Answer modes | Beginner/Standard/Expert/PQL | `utils/prompts.py` |
| ✅ Streaming responses | Groq streaming API | `app.py` |
| ✅ Always-visible panel | st.columns (no sidebar collapse) | `components/left_panel.py` |
| ✅ Source attribution | Expander with URLs + scores | `app.py` |
| ✅ Token + cost display | Session stats in left panel | `components/left_panel.py` |

---

## 📈 Upgrade Path to Full SaaS

### Already Done ✅
- Auth (Supabase)
- Rate limiting by tier
- Logging + monitoring
- RAG + real web search

### Next Steps for Public Launch 🔜
1. **Billing** — Add Stripe with `stripe` Python SDK. Gate `pro` tier behind payment.
2. **Analytics** — Add PostHog or Mixpanel for usage tracking.
3. **Chat persistence** — Save conversations to Supabase `chats` table.
4. **Admin dashboard** — New Streamlit page at `pages/admin.py`.
5. **Custom domain** — Point your domain to Streamlit Cloud or deploy to Railway/Render.

---

## 🛡️ Rate Limits

| Tier | Requests | Window |
|------|----------|--------|
| Free | 10 | 1 hour |
| Pro | 100 | 1 hour |
| Admin | 999 | 1 hour |

Upgrade tier by updating the `tier` column in your Supabase `profiles` table.

---

## 📝 Logs

Logs are written to `logs/` directory:
- `app_YYYY-MM-DD.log` — all events, rotated daily, kept 30 days
- `errors.log` — errors only, kept 90 days

Each query logs: `user_id | model | tokens | latency_ms | query`
