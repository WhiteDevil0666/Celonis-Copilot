# ⚡ Celonis AI Agent — Groq + Streamlit

An AI-powered Celonis assistant that fetches **real-time documentation** from
`docs.celonis.com` and delivers enhanced, expert-level answers using **Groq's
ultra-fast LLMs** with built-in web search.

---

## 🗂️ Project Structure

```
celonis-ai-agent/
├── app.py                   ← Main Streamlit app
├── requirements.txt         ← groq + streamlit
└── .streamlit/
    └── secrets.toml         ← Your Groq API key (never commit this!)
```

---

## 🚀 Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Groq API key to .streamlit/secrets.toml
#    (or just paste it in the sidebar at runtime)

# 3. Run
streamlit run app.py
```

Open http://localhost:8501

---

## ☁️ Deploy to Streamlit Cloud (Free Hosting)

1. **Push to GitHub** (make sure `.streamlit/secrets.toml` is in `.gitignore`)

2. Go to **https://share.streamlit.io** → "New app"
   - Repo: your GitHub repo
   - Branch: `main`
   - Main file: `app.py`

3. Under **Advanced → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
   ```

4. Click **Deploy** 🎉

---

## 🔑 Groq API Key

- 100% **FREE** to get: https://console.groq.com
- No credit card required for the free tier
- Free tier includes: ~30 requests/min on most models

---

## 🤖 Supported Models

| Model | Web Search | Best For |
|-------|-----------|----------|
| `groq/compound` | ✅ Built-in | Live docs fetch — **recommended** |
| `llama-3.3-70b-versatile` | ❌ | Fast, general Celonis Q&A |
| `meta/llama-4-scout-17b` | ❌ | Lightweight, quick answers |
| `mixtral-8x7b-32768` | ❌ | Long context, detailed answers |

> **Tip:** Use `groq/compound` for the most accurate, up-to-date answers
> since it automatically searches the web including docs.celonis.com.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🔍 Live web search | `groq/compound` fetches real Celonis docs |
| ⚡ Streaming responses | Tokens stream in real-time |
| 💬 Multi-turn memory | Remembers last 20 messages |
| 📋 9 Quick questions | Sidebar shortcuts for common Celonis topics |
| 🎨 Dark UI | Celonis-branded dark theme |
| 🔑 Flexible auth | API key via sidebar or secrets |
| 📊 Token counter | Tracks usage in sidebar |
| 🔄 Model switcher | Swap models at any time |
