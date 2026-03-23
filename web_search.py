"""
utils/web_search.py
REAL web search using Tavily API — focused on docs.celonis.com.
Tavily is purpose-built for AI agents (better than raw Google/Bing for RAG).
Free tier: 1,000 searches/month. Get key at: https://app.tavily.com
"""

import streamlit as st
from utils.logger import logger

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


def get_tavily_client() -> "TavilyClient | None":
    """Return Tavily client from secrets or session state."""
    api_key = (
        st.session_state.get("tavily_key")
        or st.secrets.get("TAVILY_API_KEY", "")
    )
    if not api_key or not TAVILY_AVAILABLE:
        return None
    return TavilyClient(api_key=api_key)


def search_celonis_docs(query: str, max_results: int = 4) -> list[dict]:
    """
    Search docs.celonis.com + community + official blog for query.
    Returns list of {title, url, content, score} dicts.
    """
    client = get_tavily_client()
    if not client:
        logger.warning("Tavily not configured — web search skipped")
        return []

    try:
        response = client.search(
            query=f"Celonis {query}",
            search_depth="advanced",
            include_domains=[
                "docs.celonis.com",
                "community.celonis.com",
                "celonis.com",
                "academy.celonis.com",
            ],
            max_results=max_results,
            include_answer=True,   # Tavily gives a synthesised answer too
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", "")[:800],   # trim long pages
                "score":   round(r.get("score", 0), 3),
            })

        logger.info(f"Web search: '{query}' → {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return []


def format_search_context(results: list[dict]) -> str:
    """
    Format search results into a context block to inject into the LLM prompt.
    """
    if not results:
        return ""

    lines = ["### 🔍 Live Celonis Documentation Context\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"**Source {i}: [{r['title']}]({r['url']})**")
        lines.append(r["content"])
        lines.append("")

    return "\n".join(lines)


def is_search_available() -> bool:
    """Check whether web search is properly configured."""
    return bool(
        TAVILY_AVAILABLE
        and (
            st.session_state.get("tavily_key")
            or st.secrets.get("TAVILY_API_KEY", "")
        )
    )
